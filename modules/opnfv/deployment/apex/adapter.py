##############################################################################
# Copyright (c) 2017 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import re

from opnfv.deployment import manager
from opnfv.utils import opnfv_logger as logger
from opnfv.utils import ssh_utils

logger = logger.Logger(__name__).getLogger()


class ApexAdapter(manager.DeploymentHandler):

    def __init__(self, installer_ip, installer_user, pkey_file):
        super(ApexAdapter, self).__init__(installer='apex',
                                          installer_ip=installer_ip,
                                          installer_user=installer_user,
                                          installer_pwd=None,
                                          pkey_file=pkey_file)

    def get_nodes(self):
        nodes = []
        cmd = "source /home/stack/stackrc;openstack server list"
        output = self.installer_node.run_cmd(cmd)
        lines = output.rsplit('\n')
        if len(lines) < 4:
            logger.info("No nodes found in the deployment.")
            return None

        for line in lines:
            roles = []
            if any(x in line for x in ['-----', 'Networks']):
                continue
            if 'controller' in line:
                roles.append(manager.Role.CONTROLLER)
            if 'compute' in line:
                roles.append(manager.Role.COMPUTE)
            if 'opendaylight' in line.lower():
                roles.append(manager.Role.OPENDAYLIGHT)

            fields = line.split('|')
            id = re.sub('[!| ]', '', fields[1]).encode()
            name = re.sub('[!| ]', '', fields[2]).encode()
            status_node = re.sub('[!| ]', '', fields[3]).encode().lower()
            ip = re.sub('[!| ctlplane=]', '', fields[4]).encode()

            ssh_client = None
            if 'active' in status_node:
                status = manager.NodeStatus.STATUS_OK
                ssh_client = ssh_utils.get_ssh_client(hostname=ip,
                                                      username='heat-admin',
                                                      pkey_file=self.pkey_file)
            elif 'error' in status_node:
                status = manager.NodeStatus.STATUS_ERROR
            elif 'off' in status_node:
                status = manager.NodeStatus.STATUS_OFFLINE
            else:
                status = manager.NodeStatus.STATUS_INACTIVE

            node = manager.Node(id, ip, name, status, roles, ssh_client)
            nodes.append(node)

        return nodes

    def get_openstack_version(self):
        cmd = 'source overcloudrc;sudo nova-manage version'
        result = self.installer_node.run_cmd(cmd)
        return result

    def get_sdn_version(self):
        cmd_descr = ("sudo yum info opendaylight 2>/dev/null|"
                     "grep Description|sed 's/^.*\: //'")
        cmd_ver = ("sudo yum info opendaylight 2>/dev/null|"
                   "grep Version|sed 's/^.*\: //'")
        description = None
        for node in self.nodes:
            if node.is_controller():
                description = node.run_cmd(cmd_descr)
                version = node.run_cmd(cmd_ver)
                break

        if description is None:
            return None
        else:
            return description + ':' + version

    def get_deployment_status(self):
        cmd = 'source stackrc;openstack stack list|grep CREATE_COMPLETE'
        result = self.installer_node.run_cmd(cmd)
        if result is None or len(result) == 0:
            return 'failed'
        else:
            return 'active'
