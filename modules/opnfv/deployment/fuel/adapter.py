##############################################################################
# Copyright (c) 2017 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
#         George Paraskevopoulos (geopar@intracom-telecom.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


from opnfv.deployment import manager
from opnfv.utils import opnfv_logger as logger
from opnfv.utils import ssh_utils

logger = logger.Logger(__name__).getLogger()


class FuelAdapter(manager.DeploymentHandler):

    def __init__(self, installer_ip, installer_user, installer_pwd):
        super(FuelAdapter, self).__init__(installer='fuel',
                                          installer_ip=installer_ip,
                                          installer_user=installer_user,
                                          installer_pwd=None,
                                          pkey_file=pkey_file)

    def _get_clusters(self):
        environments = []
        output = self.runcmd_fuel_env()
        lines = output.rsplit('\n')
        if len(lines) < 2:
            logger.info("No environments found in the deployment.")
            return None
        else:
            fields = lines[0].rsplit(' | ')

            index_id = -1
            index_status = -1
            index_name = -1
            index_release_id = -1

            for i in range(len(fields)):
                if "id" in fields[i]:
                    index_id = i
                elif "status" in fields[i]:
                    index_status = i
                elif "name" in fields[i]:
                    index_name = i
                elif "release_id" in fields[i]:
                    index_release_id = i

            # order env info
            for i in range(2, len(lines)):
                fields = lines[i].rsplit(' | ')
                dict = {"id": fields[index_id].strip(),
                        "status": fields[index_status].strip(),
                        "name": fields[index_name].strip(),
                        "release_id": fields[index_release_id].strip()}
                environments.append(dict)

        return environments

    def get_nodes(self, options=None):

        if options and options['cluster'] and len(self.nodes) > 0:
            n = []
            for node in self.nodes:
                if str(node.info['cluster']) == str(options['cluster']):
                    n.append(node)
            return n

        try:
            # if we have retrieved previously all the nodes, don't do it again
            # This fails the first time when the constructor calls this method
            # therefore the try/except
            if len(self.nodes) > 0:
                return self.nodes
        except:
            pass

        nodes = []
        cmd = 'fuel node'
        output = self.installer_node.run_cmd(cmd)
        lines = output.rsplit('\n')
        if len(lines) < 2:
            logger.info("No nodes found in the deployment.")
            return nodes

        # get fields indexes
        fields = lines[0].rsplit(' | ')

        index_id = -1
        index_status = -1
        index_name = -1
        index_cluster = -1
        index_ip = -1
        index_mac = -1
        index_roles = -1
        index_online = -1

        for i in range(len(fields)):
            if "group_id" in fields[i]:
                break
            elif "id" in fields[i]:
                index_id = i
            elif "status" in fields[i]:
                index_status = i
            elif "name" in fields[i]:
                index_name = i
            elif "cluster" in fields[i]:
                index_cluster = i
            elif "ip" in fields[i]:
                index_ip = i
            elif "mac" in fields[i]:
                index_mac = i
            elif "roles " in fields[i] and "pending_roles" not in fields[i]:
                index_roles = i
            elif "online" in fields[i]:
                index_online = i

        # order nodes info
        for i in range(2, len(lines)):
            fields = lines[i].rsplit(' | ')
            id = fields[index_id].strip().encode()
            ip = fields[index_ip].strip().encode()
            status_node = fields[index_status].strip().encode().lower()
            name = fields[index_name].strip().encode()
            roles_all = fields[index_roles].strip().encode().lower()

            roles = [x for x in [manager.Role.CONTROLLER,
                                 manager.Role.COMPUTE,
                                 manager.Role.ODL] if x in roles_all]

            dict = {"cluster": fields[index_cluster].strip().encode(),
                    "mac": fields[index_mac].strip().encode(),
                    "status_node": status_node,
                    "online": fields[index_online].strip().encode()}

            ssh_client = None
            if status_node == 'ready':
                status = manager.NodeStatus.STATUS_OK
                proxy = {'ip': self.installer_ip,
                         'username': self.installer_user,
                         'password': self.installer_pwd}
                ssh_client = ssh_utils.get_ssh_client(hostname=ip,
                                                      username='root',
                                                      proxy=proxy)
            elif 'error' in status_node:
                status = manager.NodeStatus.STATUS_ERROR
            elif 'off' in status_node:
                status = manager.NodeStatus.STATUS_OFFLINE
            elif 'discover' in status_node:
                status = manager.NodeStatus.STATUS_UNUSED
            else:
                status = manager.NodeStatus.STATUS_INACTIVE

            node = manager.Node(
                id, ip, name, status, roles, ssh_client, dict)
            if options and options['cluster']:
                if fields[index_cluster].strip() == options['cluster']:
                    nodes.append(node)
            else:
                nodes.append(node)

        self.get_nodes_called = True
        return nodes

    def get_openstack_version(self):
        cmd = 'source openrc;nova-manage version 2>/dev/null'
        version = None
        for node in self.nodes:
            if node.is_controller() and node.is_active():
                version = node.run_cmd(cmd)
                break
        return version

    def get_sdn_version(self):
        cmd = "apt-cache policy opendaylight|grep Installed"
        version = None
        for node in self.nodes:
            if manager.Role.ODL in node.roles and node.is_active():
                odl_version = node.run_cmd(cmd)
                if odl_version:
                    version = 'OpenDaylight ' + odl_version.split(' ')[-1]
                    break
        return version

    def get_deployment_status(self):
        cmd = "fuel env|tail -1|awk '{print $3}'"
        result = self.installer_node.run_cmd(cmd)
        if result is None or len(result) == 0:
            return 'unknown'
        elif 'operational' in result:
            return 'active'
        elif 'deploy' in result:
            return 'deploying'
        else:
            return 'active'
