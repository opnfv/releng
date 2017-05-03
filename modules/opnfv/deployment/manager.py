##############################################################################
# Copyright (c) 2017 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from abc import abstractmethod
import os
import time


from opnfv.utils import opnfv_logger as logger
from opnfv.utils import ssh_utils


logger = logger.Logger(__name__).getLogger()


class Deployment(object):

    def __init__(self,
                 installer,
                 installer_ip,
                 scenario,
                 pod,
                 status,
                 openstack_version,
                 sdn_controller,
                 nodes=None):

        self.deployment_info = {
            'installer': installer,
            'installer_ip': installer_ip,
            'scenario': scenario,
            'pod': pod,
            'status': status,
            'openstack_version': openstack_version,
            'sdn_controller': sdn_controller,
            'nodes': nodes
        }

    def _get_openstack_release(self):
        '''
        Translates an openstack version into the release name
        '''
        os_versions = {
            '12': 'Liberty',
            '13': 'Mitaka',
            '14': 'Newton',
            '15': 'Ocata',
            '16': 'Pike',
            '17': 'Queens'
        }
        try:
            version = self.deployment_info['openstack_version'].split('.')[0]
            name = os_versions[version]
            return name
        except Exception:
            return 'Unknown release'

    def get_dict(self):
        '''
        Returns a dictionary will all the attributes
        '''
        return self.deployment_info

    def __str__(self):
        '''
        Override of the str method
        '''
        s = '''
        INSTALLER:    {installer}
        SCENARIO:     {scenario}
        INSTALLER IP: {installer_ip}
        POD:          {pod}
        STATUS:       {status}
        OPENSTACK:    {openstack_version} ({openstack_release})
        SDN:          {sdn_controller}
        NODES:
    '''.format(installer=self.deployment_info['installer'],
               scenario=self.deployment_info['scenario'],
               installer_ip=self.deployment_info['installer_ip'],
               pod=self.deployment_info['pod'],
               status=self.deployment_info['status'],
               openstack_version=self.deployment_info[
            'openstack_version'],
            openstack_release=self._get_openstack_release(),
            sdn_controller=self.deployment_info['sdn_controller'])

        for node in self.deployment_info['nodes']:
            s += '{node_object}\n'.format(node_object=node)

        return s


class Role():
    INSTALLER = 'installer'
    CONTROLLER = 'controller'
    COMPUTE = 'compute'
    ODL = 'opendaylight'
    ONOS = 'onos'


class NodeStatus():
    STATUS_OK = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_OFFLINE = 'offline'
    STATUS_ERROR = 'error'
    STATUS_UNUSED = 'unused'
    STATUS_UNKNOWN = 'unknown'


class Node(object):

    def __init__(self,
                 id,
                 ip,
                 name,
                 status,
                 roles=None,
                 ssh_client=None,
                 info=None):
        self.id = id
        self.ip = ip
        self.name = name
        self.status = status
        self.ssh_client = ssh_client
        self.roles = roles
        self.info = info

        self.cpu_info = 'unknown'
        self.memory = 'unknown'
        self.ovs = 'unknown'

        if ssh_client and Role.INSTALLER not in self.roles:
            sys_info = self.get_system_info()
            self.cpu_info = sys_info['cpu_info']
            self.memory = sys_info['memory']
            self.ovs = self.get_ovs_info()

    def get_file(self, src, dest):
        '''
        SCP file from a node
        '''
        if self.status is not NodeStatus.STATUS_OK:
            logger.info("The node %s is not active" % self.ip)
            return 1
        logger.info("Fetching %s from %s" % (src, self.ip))
        get_file_result = ssh_utils.get_file(self.ssh_client, src, dest)
        if get_file_result is None:
            logger.error("SFTP failed to retrieve the file.")
        else:
            logger.info("Successfully copied %s:%s to %s" %
                        (self.ip, src, dest))
        return get_file_result

    def put_file(self, src, dest):
        '''
        SCP file to a node
        '''
        if self.status is not NodeStatus.STATUS_OK:
            logger.info("The node %s is not active" % self.ip)
            return 1
        logger.info("Copying %s to %s" % (src, self.ip))
        put_file_result = ssh_utils.put_file(self.ssh_client, src, dest)
        if put_file_result is None:
            logger.error("SFTP failed to retrieve the file.")
        else:
            logger.info("Successfully copied %s to %s:%s" %
                        (src, dest, self.ip))
        return put_file_result

    def _recv(self, function):
        output = ''
        while True:
            out = function(4096)
            if out == '':
                break
            output += out
        return output

    def run_cmd(self, cmd, check_exit_code=[0]):
        '''
        Run command remotely on a node
        '''
        if self.status is not NodeStatus.STATUS_OK:
            logger.error(
                "Error running command %s. The node %s is not active"
                % (cmd, self.ip))
            return None
        logger.debug("Running command {} on Node {}".format(cmd, self.ip))
        channel = self.ssh_client.get_transport().open_session()
        channel.exec_command(cmd)
        first_time = True
        timeout = timeout_orig = 300
        while not channel.exit_status_ready():
            if first_time and (timeout_orig - timeout) > 10:
                logger.info("The command: \"{}\" seem to take longer waiting "
                            "for return code. (Max waiting {} seconds)"
                            "".format(cmd, timeout_orig))
                first_time = False
            time.sleep(1)
            timeout -= 1
            if timeout < 0:
                raise Exception("Command \"{}\" did not end after {}.")
        if not first_time:
            logger.info("The command: \"{}\" did end after {} seconds"
                        "".format(cmd, timeout_orig - timeout))
        rc = channel.recv_exit_status()
        stdout = self._recv(channel.recv).rstrip()
        stderr = self._recv(channel.recv_stderr)
        if rc not in check_exit_code:
            logger.error("Return Code of command {} was {}. Stdout: {}, "
                         "Error: {}".format(cmd, rc, stdout, stderr))
            return stdout
        return stdout

    def get_dict(self):
        '''
        Returns a dictionary with all the attributes
        '''
        return {
            'id': self.id,
            'ip': self.ip,
            'name': self.name,
            'status': self.status,
            'roles': self.roles,
            'cpu_info': self.cpu_info,
            'memory': self.memory,
            'ovs': self.ovs,
            'info': self.info
        }

    def is_active(self):
        '''
        Returns if the node is active
        '''
        if self.status == NodeStatus.STATUS_OK:
            return True
        return False

    def is_controller(self):
        '''
        Returns if the node is a controller
        '''
        return Role.CONTROLLER in self.roles

    def is_compute(self):
        '''
        Returns if the node is a compute
        '''
        return Role.COMPUTE in self.roles

    def is_odl(self):
        '''
        Returns if the node is an opendaylight
        '''
        return Role.ODL in self.roles

    def is_onos(self):
        '''
        Returns if the node is an ONOS
        '''
        return Role.ONOS in self.roles

    def get_ovs_info(self):
        '''
        Returns the ovs version installed
        '''
        if self.is_active():
            cmd = "ovs-vsctl --version|head -1| sed 's/^.*) //'"
            return self.run_cmd(cmd)
        return None

    def get_system_info(self):
        '''
        Returns the ovs version installed
        '''
        cmd = 'grep MemTotal /proc/meminfo'
        memory = self.run_cmd(cmd).partition('MemTotal:')[-1].strip().encode()

        cpu_info = {}
        cmd = 'lscpu'
        result = self.run_cmd(cmd)
        for line in result.splitlines():
            if line.startswith('CPU(s)'):
                cpu_info['num_cpus'] = line.split(' ')[-1].encode()
            elif line.startswith('Thread(s) per core'):
                cpu_info['threads/core'] = line.split(' ')[-1].encode()
            elif line.startswith('Core(s) per socket'):
                cpu_info['cores/socket'] = line.split(' ')[-1].encode()
            elif line.startswith('Model name'):
                cpu_info['model'] = line.partition(
                    'Model name:')[-1].strip().encode()
            elif line.startswith('Architecture'):
                cpu_info['arch'] = line.split(' ')[-1].encode()

        return {'memory': memory, 'cpu_info': cpu_info}

    def __str__(self):
        return '''
            name:    {name}
            id:      {id}
            ip:      {ip}
            status:  {status}
            roles:   {roles}
            cpu:     {cpu_info}
            memory:  {memory}
            ovs:     {ovs}
            info:    {info}'''.format(name=self.name,
                                      id=self.id,
                                      ip=self.ip,
                                      status=self.status,
                                      roles=self.roles,
                                      cpu_info=self.cpu_info,
                                      memory=self.memory,
                                      ovs=self.ovs,
                                      info=self.info)


class DeploymentHandler(object):

    EX_OK = os.EX_OK
    EX_ERROR = os.EX_SOFTWARE
    FUNCTION_NOT_IMPLEMENTED = "Function not implemented by adapter!"

    def __init__(self,
                 installer,
                 installer_ip,
                 installer_user,
                 installer_pwd=None,
                 pkey_file=None):

        self.installer = installer.lower()
        self.installer_ip = installer_ip
        self.installer_user = installer_user
        self.installer_pwd = installer_pwd
        self.pkey_file = pkey_file

        if pkey_file is not None and not os.path.isfile(pkey_file):
            raise Exception(
                'The private key file %s does not exist!' % pkey_file)

        self.installer_connection = ssh_utils.get_ssh_client(
            hostname=self.installer_ip,
            username=self.installer_user,
            password=self.installer_pwd,
            pkey_file=self.pkey_file)

        if self.installer_connection:
            self.installer_node = Node(id='',
                                       ip=installer_ip,
                                       name=installer,
                                       status=NodeStatus.STATUS_OK,
                                       ssh_client=self.installer_connection,
                                       roles=Role.INSTALLER)
        else:
            raise Exception(
                'Cannot establish connection to the installer node!')

        self.nodes = self.get_nodes()

    @abstractmethod
    def get_openstack_version(self):
        '''
        Returns a string of the openstack version (nova-compute)
        '''
        raise Exception(DeploymentHandler.FUNCTION_NOT_IMPLEMENTED)

    @abstractmethod
    def get_sdn_version(self):
        '''
        Returns a string of the sdn controller and its version, if exists
        '''
        raise Exception(DeploymentHandler.FUNCTION_NOT_IMPLEMENTED)

    @abstractmethod
    def get_deployment_status(self):
        '''
        Returns a string of the status of the deployment
        '''
        raise Exception(DeploymentHandler.FUNCTION_NOT_IMPLEMENTED)

    @abstractmethod
    def get_nodes(self, options=None):
        '''
            Generates a list of all the nodes in the deployment
        '''
        raise Exception(DeploymentHandler.FUNCTION_NOT_IMPLEMENTED)

    def get_installer_node(self):
        '''
            Returns the installer node object
        '''
        return self.installer_node

    def get_arch(self):
        '''
            Returns the architecture of the first compute node found
        '''
        arch = None
        for node in self.nodes:
            if node.is_compute():
                arch = node.cpu_info.get('arch', None)
                if arch:
                    break
        return arch

    def get_deployment_info(self):
        '''
            Returns an object of type Deployment
        '''
        return Deployment(installer=self.installer,
                          installer_ip=self.installer_ip,
                          scenario=os.getenv('DEPLOY_SCENARIO', 'Unknown'),
                          status=self.get_deployment_status(),
                          pod=os.getenv('NODE_NAME', 'Unknown'),
                          openstack_version=self.get_openstack_version(),
                          sdn_controller=self.get_sdn_version(),
                          nodes=self.nodes)
