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


logger = logger.Logger("Deployment Manager").getLogger()


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

    def _get_openstack_name(self):
        name = ''
        if '12' in self.deployment_info['openstack_version']:
            name = 'Liberty'
        elif '13' in self.deployment_info['openstack_version']:
            name = 'Mitaka'
        elif '14' in self.deployment_info['openstack_version']:
            name = 'Newton'
        elif '15' in self.deployment_info['openstack_version']:
            name = 'Ocata'
        elif '16' in self.deployment_info['openstack_version']:
            name = 'Pike'
        elif '17' in self.deployment_info['openstack_version']:
            name = 'Queens'

        return name

    def get_deployment_dict(self):
        return self.deployment_info

    def __str__(self):
        s = ''
        s += ("INSTALLER:    %s\n" % self.deployment_info['installer'])
        s += ("SCENARIO:     %s\n" % self.deployment_info['scenario'])
        s += ("INSTALLER IP: %s\n" % self.deployment_info['installer_ip'])
        s += ("POD:          %s\n" % self.deployment_info['pod'])
        s += ("STATUS:       %s\n" % self.deployment_info['status'])
        s += ("OPENSTACK:    %s (%s)\n"
              % (self.deployment_info['openstack_version'],
                 self._get_openstack_name()))
        s += ("SDN:          %s\n" % self.deployment_info['sdn_controller'])
        s += ("NODES:\n")

        for node in self.deployment_info['nodes']:
            s += '\t%s\n' % node

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
        return {
            'id': self.id,
            'ip': self.ip,
            'name': self.name,
            'status': self.status,
            'roles': self.roles,
            'info': self.info
        }

    def get_attribute(self, attribute):
        return self.get_dict()[attribute]

    def is_controller(self):
        if 'controller' in self.get_attribute('roles'):
            return True
        return False

    def __str__(self):
        return str(self.get_dict())


class DeploymentHandler(object):

    EX_OK = os.EX_OK
    EX_ERROR = os.EX_SOFTWARE
    EX_INSTALLER_NOT_SUPPORTED = os.EX_SOFTWARE - 1
    FUNCTION_NOT_IMPLEMENTED = "Function not implemented by adapter!"
    INSTALLERS = ["fuel", "apex", "compass", "joid", "daisy"]

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

        if self.installer not in DeploymentHandler.INSTALLERS:
            logger.error("Installer %s is  not supported. "
                         "Please use one of the following: %s"
                         % (self.installer, DeploymentHandler.INSTALLERS))
            return DeploymentHandler.EX_INSTALLER_NOT_SUPPORTED

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
        raise DeploymentHandler.FUNCTION_NOT_IMPLEMENTED

    @abstractmethod
    def get_sdn_version(self):
        raise DeploymentHandler.FUNCTION_NOT_IMPLEMENTED

    @abstractmethod
    def get_deployment_status(self):
        raise DeploymentHandler.FUNCTION_NOT_IMPLEMENTED

    @abstractmethod
    def nodes(self, options=None):
        '''
            Returns a list of Node objects
            Must be implemented by the each handler
        '''
        raise DeploymentHandler.FUNCTION_NOT_IMPLEMENTED

    def get_nodes(self, options=None):
        return self.nodes

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
