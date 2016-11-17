##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


import libvirt
import re
import subprocess
import xml.etree.ElementTree as ET

import opnfv.modules.utils.SSHUtils as ssh_utils
import opnfv.modules.utils.OPNFVLogger as logger


class ApexAdapter:

    def __init__(self, user="root"):
        self.logger = logger.Logger("ApexHandler").getLogger()
        self.installer_ip = self.get_ip_from_installer()
        self.installer_connection = ssh_utils.get_ssh_client(
            self.installer_ip,
            self.installer_user)

    def get_ip_from_installer(self):
        conn = libvirt.openReadOnly(None)
        if conn == None:
            raise Exception('Failed to open connection to the hypervisor')

        try:
            undercloud_vm = conn.lookupByName("undercloud")
        except:
            try:
                undercloud_vm = conn.lookupByName("instack")
            except:
                raise Exception('Failed to find undercloud')

        xml = undercloud_vm.XMLDesc(0)
        root = ET.fromstring(xml)
        interface = root.findall("./devices/interface")[0]
        mac = interface.find("mac")
        mac_address = mac.get("address")
        print mac_address

        process = subprocess.Popen(['/usr/sbin/arp', '-a'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        process.wait()
        for line in process.stdout:
            if mac_address in line:
                ip_address = re.search(
                    r'(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', line)
                print 'VM {0} with MAC Address {1} is using IP {2}'.format(
                    vm.name(), mac_address, ip_address.groups(0)[0]
                )
            else:
                print("Cannot find IP of undercloud in the ARP table")

    def get_deployment_info(self):
        pass

    def get_nodes(self):
        pass

    def get_controller_ips(self):
        pass

    def get_compute_ips(self):
        pass

    def get_file_from_installer(self, origin, target, options=None):
        pass

    def get_file_from_controller(self, origin, target, ip=None, options=None):
        pass
