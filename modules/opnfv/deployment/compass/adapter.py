#!/usr/bin/env python

# Copyright (c) 2017 HUAWEI TECHNOLOGIES CO.,LTD and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

import re

from opnfv.deployment import manager
from opnfv.utils import opnfv_logger as logger
from opnfv.utils import ssh_utils

logger = logger.Logger(__name__).getLogger()


class CompassAdapter(manager.DeploymentHandler):

    def __init__(self, installer_ip, installer_user, installer_pwd):
        super(CompassAdapter, self).__init__(installer='compass',
                                             installer_ip=installer_ip,
                                             installer_user=installer_user,
                                             installer_pwd=installer_pwd,
                                             pkey_file=None)
        self.num_nodes = 0

    def get_nodes(self, options=None):
        nodes = []
        node_match_detail = ("Hostname", "IP Address", "MAC Address")
        node_match_keys = "|".join(node_match_detail)
        cmd = ("cobbler system report | grep -E '%s' "
               "| awk -F ' : ' '{print $2}'" % (node_match_keys))
        output = self.installer_node.run_cmd(cmd)
        lines = output.rsplit('\n')
        if output and len(output) < 2:
            logger.info("No nodes found in the deployment.")
            return nodes

        iter_num = len(node_match_detail)
        for i in range(self.num_nodes):
            name = lines[iter_num * i].strip().encode()
            ip = lines[iter_num * i + 1].strip().encode()
            mac_dict = {"mac": lines[iter_num * i + 2].strip().encode()}

            roles = ""
            controller_hosts = ("host1", "host2", "host3")
            compute_hosts = ("host4", "host5")
            if name in controller_hosts:
                roles = manager.Role.CONTROLLER
            elif name in compute_hosts:
                roles = manager.Role.COMPUTE

            ssh_client = None
            status = manager.NodeStatus.STATUS_OK
            proxy = {'ip': self.installer_ip,
                     'username': self.installer_user,
                     'password': self.installer_pwd}
            ssh_client = ssh_utils.get_ssh_client(hostname=ip,
                                                  username='root',
                                                  proxy=proxy)
            node = manager.Node(
                None, ip, name, status, roles, ssh_client, mac_dict)
            nodes.append(node)

        self.get_nodes_called = True
        return nodes

    def get_openstack_version(self):
        version = None
        cmd = '. /opt/admin-openrc.sh;nova-manage version 2>/dev/null'
        for node in self.nodes:
            if node.is_controller() and node.name == 'host1':
                version = node.run_cmd(cmd)
                break
        return version

    def get_sdn_version(self):
        try:
            sdn_info = self._get_sdn_info('OpenDaylight')
            if sdn_info is None:
                sdn_info = self._get_sdn_info('ONOS')
            return sdn_info
        except Exception as e:
            logger.error(e)

    def _get_sdn_info(self, sdn_type):
        if sdn_type == 'OpenDaylight':
            sdn_key = 'distribution-karaf'
        elif sdn_type == 'ONOS':
            sdn_key = 'onos-'
        else:
            raise KeyError('SDN %s is not supported', sdn_type)

        cmd = "find /opt -name '{0}*'".format(sdn_key)
        sdn_info = None
        for node in self.nodes:
            if node.is_controller():
                sdn_info = node.run_cmd(cmd)
                break

        sdn_version = None
        if sdn_info:
            match_sdn = re.findall(r".*0\.(\d\.\d).*", sdn_info)
            if (match_sdn and len(match_sdn) >= 1):
                sdn_version = match_sdn[0]
                sdn_version = '{0} {1}'.format(sdn_type, sdn_version)
        return sdn_version

    def get_deployment_status(self):
        cmd = ("cobbler system report | grep Hostname | wc -l")
        self.num_nodes = int(self.installer_node.run_cmd(cmd))
        cmd = ('mysql -ucompass -pcompass -Dcompass '
               '-e"select * from clusterhost_state;" '
               '2>&1 | grep -v "Warning: Using a password"'
               "| grep 'SUCCESSFUL'| wc -l")
        result = self.installer_node.run_cmd(cmd)
        if result is None or len(result) == 0:
            return 'failed'
        elif int(result) == self.num_nodes:
            return 'active'
        elif int(result) < self.num_nodes:
            num_failed = self.num_nodes - int(result)
            return ('{0} nodes are active, {1} nodes failed'
                    .format(result, str(num_failed)))
