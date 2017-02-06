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
                 nodes=[]):

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
        except Exception as e:
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
        NODES:'''.format(installer=self.deployment_info['installer'],
                         scenario=self.deployment_info['scenario'],
                         installer_ip=self.deployment_info['installer_ip'],
                         pod=self.deployment_info['pod'],
                         status=self.deployment_info['status'],
                         openstack_version=self.deployment_info[
            'openstack_version'],
            openstack_release=self._get_openstack_release(),
            sdn_controller=self.deployment_info['sdn_controller'])
        s += '\n'
        for node in self.deployment_info['nodes']:
            s += '\t\t%s\n' % node

        return s


class Node(object):

    STATUS_OK = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_OFFLINE = 'offline'
    STATUS_FAILED = 'failed'

    def __init__(self,
                 id,
                 ip,
                 name,
                 status,
                 roles,
                 ssh_client,
                 info={}):
        self.id = id
        self.ip = ip
        self.name = name
        self.status = status
        self.ssh_client = ssh_client
        self.roles = roles
        self.info = info

    def get_file(self, src, dest):
        '''
        SCP file from a node
        '''
        if self.status is not Node.STATUS_OK:
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
        if self.status is not Node.STATUS_OK:
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

    def run_cmd(self, cmd):
        '''
        Run command remotely on a node
        '''
        if self.status is not Node.STATUS_OK:
            logger.info("The node %s is not active" % self.ip)
            return 1
        _, stdout, stderr = (self.ssh_client.exec_command(cmd))
        error = stderr.readlines()
        if len(error) > 0:
            logger.error("error %s" % ''.join(error))
            return error
        output = ''.join(stdout.readlines()).rstrip()
        return output

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
            'info': self.info
        }

    def get_attribute(self, attribute):
        '''
        Returns an attribute given the name
        '''
        return self.get_dict()[attribute]

    def is_controller(self):
        '''
        Returns if the node is a controller
        '''
        if 'controller' in self.get_attribute('roles'):
            return True
        return False

    def is_compute(self):
        '''
        Returns if the node is a controller
        '''
        if 'compute' in self.get_attribute('roles'):
            return True
        return False

    def __str__(self):
        return str(self.get_dict())


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
                                       status='active',
                                       ssh_client=self.installer_connection,
                                       roles='installer node')
        else:
            raise Exception(
                'Cannot establish connection to the installer node!')

        self.nodes = self.nodes()

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
    def nodes(self, options=None):
        '''
            Generates a list of all the nodes in the deployment
        '''
        raise Exception(DeploymentHandler.FUNCTION_NOT_IMPLEMENTED)

    def get_nodes(self, options=None):
        '''
            Returns the list of Node objects
        '''
        return self.nodes

    def get_installer_node(self):
        '''
            Returns the installer node object
        '''
        return self.installer_node

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
