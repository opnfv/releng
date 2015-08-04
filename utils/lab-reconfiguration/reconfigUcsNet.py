#!/usr/bin/python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script reconfigure UCSM vnics for varios OPNFV deployers
# Usage: reconfigUcsNet.py [options]
#
# Options:
# -h, --help            show this help message and exit
# -i IP, --ip=IP        [Mandatory] UCSM IP Address
# -u USERNAME, --username=USERNAME
#                       [Mandatory] Account Username for UCSM Login
# -p PASSWORD, --password=PASSWORD
#                       [Mandatory] Account Password for UCSM Login
# -f FILE, --file=FILE
#                       [Optional] Yaml file with network config you want to set for POD
#                       If not present only current network config will be printed
#

import getpass
import optparse
import platform
import yaml
import time
from UcsSdk import *
from collections import defaultdict

POD_PREFIX = "POD-2"
INSTALLER = "POD-21"

def getpassword(prompt):
    if platform.system() == "Linux":
        return getpass.unix_getpass(prompt=prompt)
    elif platform.system() == "Windows" or platform.system() == "Microsoft":
        return getpass.win_getpass(prompt=prompt)
    else:
        return getpass.getpass(prompt=prompt)


def get_servers(handle=None):
    """
    Return list of servers
    """
    orgObj = handle.GetManagedObject(None, OrgOrg.ClassId(), {OrgOrg.DN : "org-root"})[0]
    servers = handle.GetManagedObject(orgObj, LsServer.ClassId())
    for server in servers:
        if server.Type == 'instance' and POD_PREFIX in server.Dn:
            yield server


def set_boot_policy(handle=None, server=None, policy=None):
    """
    Modify Boot policy of server
    """
    obj = handle.GetManagedObject(None, LsServer.ClassId(), {
            LsServer.DN: server.Dn})
    handle.SetManagedObject(obj, LsServer.ClassId(), {
            LsServer.BOOT_POLICY_NAME: policy} )
    print " Configured boot policy: {}".format(policy)


def ack_pending(handle=None, server=None):
    """
    Acknowledge pending state of server
    """
    handle.AddManagedObject(server, LsmaintAck.ClassId(), {
            LsmaintAck.DN: server.Dn + "/ack",
            LsmaintAck.DESCR:"",
            LsmaintAck.ADMIN_STATE:"trigger-immediate",
            LsmaintAck.SCHEDULER:"",
            LsmaintAck.POLICY_OWNER:"local"}, True)
    print " Pending-reboot -> Acknowledged."


def get_vnics(handle=None, server=None):
    """
    Return list of vnics for given server
    """
    vnics = handle.ConfigResolveChildren(VnicEther.ClassId(), server.Dn, None, YesOrNo.TRUE)
    return vnics.OutConfigs.GetChild()


def get_network_config(handle=None):
    """
    Print current network config
    """
    print "\nCURRENT NETWORK CONFIG:"
    print " d - default, t - tagged"
    for server in get_servers(handle):
        print ' {}'.format(server.Name)
        print '  Boot policy: {}'.format(server.OperBootPolicyName)
        for vnic in get_vnics(handle, server):
            print '  {}'.format(vnic.Name)
            print '   {}'.format(vnic.Addr)
            vnicIfs = handle.ConfigResolveChildren(VnicEtherIf.ClassId(), vnic.Dn, None, YesOrNo.TRUE)
            for vnicIf in vnicIfs.OutConfigs.GetChild():
                if vnicIf.DefaultNet == 'yes':
                    print '    Vlan: {}d'.format(vnicIf.Vnet)
                else:
                    print '    Vlan: {}t'.format(vnicIf.Vnet)


def add_interface(handle=None, lsServerDn=None, vnicEther=None, templName=None, order=None, macAddr=None):
    """
    Add interface to server specified by server.DN name
    """
    print " Adding interface: {}, template: {}, server.Dn: {}".format(vnicEther, templName, lsServerDn)
    obj = handle.GetManagedObject(None, LsServer.ClassId(), {LsServer.DN:lsServerDn})
    vnicEtherDn = lsServerDn + "/ether-" + vnicEther
    params = {
        VnicEther.STATS_POLICY_NAME: "default",
        VnicEther.NAME: vnicEther,
        VnicEther.DN: vnicEtherDn,
        VnicEther.SWITCH_ID: "A-B",
        VnicEther.ORDER: order,
        "adminHostPort": "ANY",
        VnicEther.ADMIN_VCON: "any",
        VnicEther.ADDR: macAddr,
        VnicEther.NW_TEMPL_NAME: templName,
        VnicEther.MTU: "1500"}
    handle.AddManagedObject(obj, VnicEther.ClassId(), params, True)


def remove_interface(handle=None, vnicEtherDn=None):
    """
    Remove interface specified by Distinguished Name (vnicEtherDn)
    """
    print " Removing interface: {}".format(vnicEtherDn)
    obj = handle.GetManagedObject(None, VnicEther.ClassId(), {VnicEther.DN:vnicEtherDn})
    handle.RemoveManagedObject(obj)


def read_yaml_file(yamlFile):
    """
    Read vnic config from yaml file
    """
    # TODO: add check if vnic templates specified in file exist on UCS
    with open(yamlFile, 'r') as stream:
        return yaml.load(stream)


def set_network(handle=None, yamlFile=None):
    """
    Configure VLANs on POD according specified network
    """
    # add interfaces and bind them with vNIC templates
    print "\nRECONFIGURING VNICs..."
    pod_data = read_yaml_file(yamlFile)
    network = pod_data['network']

    for index, server in enumerate(get_servers(handle)):
        # Assign template to interface
        for iface, data in network.iteritems():
            add_interface(handle, server.Dn, iface, data['template'], data['order'], data['mac-list'][index])

        # Remove other interfaces which have not assigned required vnic template
        vnics = get_vnics(handle, server)
        for vnic in vnics:
            if not any(data['template'] in vnic.OperNwTemplName for iface, data in network.iteritems()):
                remove_interface(handle, vnic.Dn)
                print "  {} removed, template: {}".format(vnic.Name, vnic.OperNwTemplName)

        # Set boot policy template
        if not INSTALLER in server.Dn:
            set_boot_policy(handle, server, pod_data['boot-policy'])


if __name__ == "__main__":
    # Latest urllib2 validate certs by default
    # The process wide "revert to the old behaviour" hook is to monkeypatch the ssl module
    # https://bugs.python.org/issue22417
    import ssl
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context
    try:
        handle = UcsHandle()
        parser = optparse.OptionParser()
        parser.add_option('-i', '--ip',dest="ip",
                        help="[Mandatory] UCSM IP Address")
        parser.add_option('-u', '--username',dest="userName",
                        help="[Mandatory] Account Username for UCSM Login")
        parser.add_option('-p', '--password',dest="password",
                        help="[Mandatory] Account Password for UCSM Login")
        parser.add_option('-f', '--file',dest="yamlFile",
                        help="[Optional] Yaml file contains network config you want to set on UCS POD1")
        (options, args) = parser.parse_args()

        if not options.ip:
            parser.print_help()
            parser.error("Provide UCSM IP Address")
        if not options.userName:
            parser.print_help()
            parser.error("Provide UCSM UserName")
        if not options.password:
            options.password=getpassword("UCSM Password:")

        handle.Login(options.ip, options.userName, options.password)

        # Change vnic template if specified in cli option
        if (options.yamlFile != None):
            set_network(handle, options.yamlFile)
            time.sleep(5)

        print "\nWait until Overall Status of all nodes is OK..."
        timeout = time.time() + 60*10   #10 minutes timeout
        while True:
            list_of_states = []
            for server in get_servers(handle):
                if server.OperState == "pending-reboot":
                    ack_pending(handle,server)
                list_of_states.append(server.OperState)
            print " {}, {} seconds remains.".format(list_of_states, round(timeout-time.time()))
            if all(state == "ok" for state in list_of_states):
                break
            if time.time() > timeout:
                raise Exception("Timeout reached while waiting for OK status.")
            time.sleep(5)

        # Show current vnic MACs and VLANs
        get_network_config(handle)

        handle.Logout()

    except Exception, err:
        handle.Logout()
        print "Exception:", str(err)
        import traceback, sys
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
