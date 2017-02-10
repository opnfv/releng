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

logger = logger.Logger("FuelAdapter").getLogger()


class FuelAdapter(manager.DeploymentHandler):

    def __init__(self, installer_ip, installer_user, installer_pwd):
        super(FuelAdapter, self).__init__(installer='fuel',
                                          installer_ip=installer_ip,
                                          installer_user=installer_user,
                                          installer_pwd=installer_pwd,
                                          pkey_file=None)

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

            for i in range(len(fields) - 1):
                if "id" in fields[i]:
                    index_id = i
                elif "status" in fields[i]:
                    index_status = i
                elif "name" in fields[i]:
                    index_name = i
                elif "release_id" in fields[i]:
                    index_release_id = i

            # order env info
            for i in range(2, len(lines) - 1):
                fields = lines[i].rsplit(' | ')
                dict = {"id": fields[index_id].strip(),
                        "status": fields[index_status].strip(),
                        "name": fields[index_name].strip(),
                        "release_id": fields[index_release_id].strip()}
                environments.append(dict)

        return environments

    def nodes(self, options=None):
        nodes = []
        cmd = 'fuel node'
        output = self.installer_node.run_cmd(cmd)
        lines = output.rsplit('\n')
        if len(lines) < 2:
            logger.info("No nodes found in the deployment.")
            return None
        else:
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

            for i in range(0, len(fields) - 1):
                if "id" in fields[i]:
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
                elif "roles " in fields[i]:
                    index_roles = i
                elif "online" in fields[i]:
                    index_online = i

            # order nodes info
            for i in range(2, len(lines) - 1):
                fields = lines[i].rsplit(' | ')

                id = fields[index_id].strip(),
                ip = fields[index_ip].strip()
                status_node = fields[index_status].strip()
                name = fields[index_name].strip()
                roles = fields[index_roles].strip()

                dict = {"cluster": fields[index_cluster].strip(),
                        "mac": fields[index_mac].strip(),
                        "online": fields[index_online].strip()}

                if status_node == 'ready':
                    status = manager.Node.STATUS_OK
                    proxy = {'ip': self.installer_ip,
                             'username': self.installer_user,
                             'password': self.installer_pwd}
                    ssh_client = ssh_utils.get_ssh_client(hostname=ip,
                                                          username='root',
                                                          proxy=proxy)
                else:
                    status = manager.Node.STATUS_INACTIVE
                    ssh_client = None

                node = manager.Node(
                    id, ip, name, status, roles, ssh_client, dict)
                nodes.append(node)

                # TODO: Add support for Fuel cluster selection
                '''
                if options and options['cluster']:
                    if fields[index_cluster].strip() == options['cluster']:
                '''

        return nodes

    def get_openstack_version(self):
        cmd = 'source openrc;nova-manage version 2>/dev/null'
        version = None
        for node in self.nodes:
            if 'controller' in node.get_attribute('roles'):
                version = node.run_cmd(cmd)
                break
        return version

    def get_sdn_version(self):
        cmd = "apt-cache show opendaylight|grep Version|sed 's/^.*\: //'"
        version = None
        for node in self.nodes:
            if 'controller' in node.get_attribute('roles'):
                odl_version = node.run_cmd(cmd)
                if odl_version:
                    version = 'OpenDaylight ' + odl_version
                break
        return version

    def get_deployment_status(self):
        cmd = 'fuel env|grep operational'
        result = self.installer_node.run_cmd(cmd)
        if result is None or len(result) == 0:
            return 'failed'
        else:
            return 'active'
