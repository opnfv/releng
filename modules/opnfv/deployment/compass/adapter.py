#!/usr/bin/env python

# Copyright (c) 2017 HUAWEI TECHNOLOGIES CO.,LTD and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

import netaddr
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

    def get_nodes(self, options=None):
        nodes = []
        self.deployment_status = None
        self.nodes_dict = self._get_deployment_nodes()
        self.deployment_status = self.get_deployment_status()

        for k, v in self.nodes_dict.iteritems():
            node = manager.Node(None, v['ip'],
                                k, v['status'],
                                v['roles'], v['ssh_client'], v['mac'])
            nodes.append(node)

        self.get_nodes_called = True
        return nodes

    def get_openstack_version(self):
        version = None
        cmd = 'source /opt/admin-openrc.sh;nova-manage version 2>/dev/null'
        for node in self.nodes:
            if node.is_controller():
                version = node.run_cmd(cmd)
                break
        return version

    def get_sdn_version(self):
        try:
            sdn_info = self._get_sdn_info(manager.Role.ODL)
            if sdn_info is None:
                sdn_info = self._get_sdn_info(manager.Role.ONOS)
            return sdn_info
        except Exception as e:
            logger.error(e)

    def _get_sdn_info(self, sdn_type):
        if sdn_type == manager.Role.ODL:
            sdn_key = 'distribution-karaf'
        elif sdn_type == manager.Role.ONOS:
            sdn_key = 'onos-'
        else:
            raise KeyError('SDN %s is not supported', sdn_type)

        cmd = "find /opt -name '{0}*'".format(sdn_key)
        sdn_info = next(node.run_cmd(cmd) for node in self.nodes
                        if node.is_controller())

        sdn_version = 'None'
        if sdn_info:
            match_sdn = re.findall(r".*0\.(\d\.\d).*", sdn_info)
            if (match_sdn and len(match_sdn) >= 1):
                sdn_version = match_sdn[0]
                sdn_version = '{0} {1}'.format(sdn_type, sdn_version)
        return sdn_version

    def get_deployment_status(self):
        if self.deployment_status is not None:
            logger.debug('Skip - Node status has been retrieved once')
            return self.deployment_status
        if not self.nodes_dict:
            self.nodes_dict = self._get_deployment_nodes()
        for k, v in self.nodes_dict.iteritems():
            if manager.Role.CONTROLLER in v['roles']:
                cmd = 'source /opt/admin-openrc.sh; nova hypervisor-list;'
                '''
                +----+---------------------+-------+---------+

                | ID | Hypervisor hostname | State | Status  |

                +----+---------------------+-------+---------+

                | 3  | host4               | up    | enabled |

                | 6  | host5               | up    | enabled |

                +----+---------------------+-------+---------+
                '''
                _, stdout, stderr = (v['ssh_client'].exec_command(cmd))
                error = stderr.readlines()
                if len(error) > 0:
                    logger.error("error %s" % ''.join(error))
                    status = manager.NodeStatus.STATUS_ERROR
                    v['status'] = status
                    continue

                lines = stdout.readlines()
                for i in range(3, len(lines) - 1):
                    fields = lines[i].strip().encode().rsplit(' | ')
                    hostname = fields[1].strip().encode().lower()
                    state = fields[2].strip().encode().lower()
                    if 'up' == state:
                        status = manager.NodeStatus.STATUS_OK
                    else:
                        status = manager.NodeStatus.STATUS_ERROR
                    self.nodes_dict[hostname]['status'] = status
                    v['status'] = manager.NodeStatus.STATUS_OK

        failed_nodes = [k for k, v in self.nodes_dict.iteritems()
                        if v['status'] != manager.NodeStatus.STATUS_OK]

        if failed_nodes and len(failed_nodes) > 0:
            return 'Hosts {0} failed'.format(','.join(failed_nodes))

        return 'active'

    def _get_deployment_nodes(self):
        sql_query = ('select host.host_id, host.roles, '
                     'network.ip_int, machine.mac from clusterhost as host, '
                     'host_network as network, machine as machine '
                     'where host.host_id=network.host_id '
                     'and host.id=machine.id;')
        cmd = 'mysql -uroot -Dcompass -e "{0}"'.format(sql_query)
        logger.debug('mysql command: %s', cmd)
        output = self.installer_node.run_cmd(cmd)
        '''
        host_id roles   ip_int  mac
        1   ["controller", "ha", "ceph-adm", "ceph-mon"]    167837746
        00:00:43:04:11:91
        2   ["controller", "ha", "ceph-mon"]    167837747   00:00:4b:ac:dc:24
        3   ["controller", "ha", "ceph-mon"]    167837748   00:00:db:7b:4f:fa
        4   ["compute", "ceph-osd"] 167837749   00:00:0a:f7:73:8c
        5   ["compute", "ceph-osd"] 167837750   00:00:6e:a5:8c:f9
        '''
        lines = output.encode().rsplit('\n')
        nodes_dict = {}
        if (not lines or len(lines) < 2):
            logger.error('No nodes are found in the deployment.')
            return nodes_dict

        proxy = {'ip': self.installer_ip,
                 'username': self.installer_user,
                 'password': self.installer_pwd}
        for i in range(1, len(lines)):
            fields = lines[i].strip().encode().rsplit('\t')
            name = 'host{0}'.format(fields[0].strip().encode())
            roles_all = fields[1].strip().encode().lower()
            roles = [x for x in [manager.Role.CONTROLLER,
                                 manager.Role.COMPUTE] if x in roles_all]
            ip = fields[2].strip().encode()
            ip = str(netaddr.IPAddress(ip))
            mac = fields[3].strip().encode()

            nodes_dict[name] = {}
            nodes_dict[name]['roles'] = roles
            nodes_dict[name]['ip'] = ip
            nodes_dict[name]['mac'] = mac
            ssh_client = ssh_utils.get_ssh_client(hostname=ip,
                                                  username='root',
                                                  proxy=proxy)
            nodes_dict[name]['ssh_client'] = ssh_client
            nodes_dict[name]['status'] = manager.NodeStatus.STATUS_UNKNOWN
        return nodes_dict
