##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


from opnfv.deployment import manager
from opnfv.utils import opnfv_logger as logger
from opnfv.utils import ssh_utils

logger = logger.Logger(__name__).getLogger()


class DaisyAdapter(manager.DeploymentHandler):

    def __init__(self, installer_ip, installer_user, installer_pwd):
        super(DaisyAdapter, self).__init__(installer='daisy',
                                           installer_ip=installer_ip,
                                           installer_user=installer_user,
                                           installer_pwd=installer_pwd,
                                           pkey_file=None)

    def _get_clusters(self):
        clusters = []
        cmd = 'source /root/daisyrc_admin; daisy cluster-list | grep -v "+--"'
        output = self.installer_node.run_cmd(cmd)
        lines = output.rsplit('\n')
        if len(lines) < 2:
            logger.info("No environments found in the deployment.")
            return None
        else:
            fields = lines[0].rsplit('|')

            index_id = -1
            index_status = -1
            index_name = -1
            index_nodes = -1

            for i in range(len(fields)):
                if "ID" in fields[i]:
                    index_id = i
                elif "Status" in fields[i]:
                    index_status = i
                elif "Name" in fields[i]:
                    index_name = i
                elif "Nodes" in fields[i]:
                    index_nodes = i

            # order env info
            for i in range(1, len(lines)):
                fields = lines[i].rsplit('|')
                dict = {"id": fields[index_id].strip(),
                        "status": fields[index_status].strip(),
                        "name": fields[index_name].strip(),
                        "nodes": fields[index_nodes].strip()}
                clusters.append(dict)

        return clusters

    def get_nodes(self, options=None):
        if hasattr(self, 'nodes') and len(self.nodes) > 0:
            if options and 'cluster' in options and options['cluster']:
                nodes = []
                for node in self.nodes:
                    if str(node.info['cluster']) == str(options['cluster']):
                        nodes.append(node)
                return nodes
            else:
                return self.nodes

        clusters = self._get_clusters()
        nodes = []
        for cluster in clusters:
            if options and 'cluster' in options and options['cluster']:
                if cluster["id"] != options['cluster']:
                    continue
            cmd = 'source /root/daisyrc_admin; daisy host-list ' \
                  '--cluster-id {} | grep -v "+--"'.format(cluster["id"])
            output = self.installer_node.run_cmd(cmd)
            lines = output.rsplit('\n')
            if len(lines) < 2:
                logger.info("No nodes found in the cluster {}".format(
                    cluster["id"]))
                continue

            fields = lines[0].rsplit('|')
            index_id = -1
            index_status = -1
            index_name = -1

            for i in range(len(fields)):
                if "ID" in fields[i]:
                    index_id = i
                elif "Role_status" in fields[i]:
                    index_status = i
                elif "Name" in fields[i]:
                    index_name = i

            for i in range(1, len(lines)):
                fields = lines[i].rsplit('|')
                id = fields[index_id].strip().encode()
                status_node = fields[index_status].strip().encode().lower()
                name = fields[index_name].strip().encode()
                ip = ".".join(name.split("-")[1:])

                cmd_role = 'source /root/daisyrc_admin; ' \
                           'daisy host-detail {} | grep "^| role"'.format(id)
                output_role = self.installer_node.run_cmd(cmd_role)
                role_all = output_role.rsplit('|')[2].strip().encode()
                roles = []
                if 'COMPUTER' in role_all:
                    roles.append(manager.Role.COMPUTE)
                if 'CONTROLLER_LB' in role_all or 'CONTROLLER_HA' in role_all:
                    roles.append(manager.Role.CONTROLLER)

                ssh_client = None
                if status_node == 'active':
                    status = manager.NodeStatus.STATUS_OK
                    proxy = {'ip': self.installer_ip,
                             'username': self.installer_user,
                             'password': self.installer_pwd,
                             'pkey_file': '/root/.ssh/id_dsa'}
                    ssh_client = ssh_utils.get_ssh_client(hostname=ip,
                                                          username='root',
                                                          proxy=proxy)
                else:
                    status = manager.NodeStatus.STATUS_INACTIVE

                node = DaisyNode(id, ip, name, status, roles, ssh_client)
                nodes.append(node)
        return nodes

    def get_openstack_version(self):
        cmd = 'docker exec nova_api nova-manage version 2>/dev/null'
        version = None
        for node in self.nodes:
            if node.is_controller() and node.is_active():
                version = node.run_cmd(cmd)
                break
        return version

    def get_sdn_version(self):
        version = None
        for node in self.nodes:
            if manager.Role.CONTROLLER in node.roles and node.is_active():
                cmd = 'docker inspect --format=\'{{.Name}}\' `docker ps -q`'
                output = node.run_cmd(cmd)
                if '/opendaylight' in output.rsplit('\n'):
                    cmd2 = 'docker exec opendaylight ' \
                           'sudo yum info opendaylight 2>/dev/null ' \
                           '| grep Version | tail -1'
                    odl_ver = node.run_cmd(cmd2)
                    if odl_ver:
                        version = 'OpenDaylight: ' + odl_ver.split(' ')[-1]
                    break
        return version

    def get_deployment_status(self):
        clusters = self._get_clusters()
        if clusters is None or len(clusters) == 0:
            return 'unknown'
        else:
            return clusters[0]['status']


class DaisyNode(manager.Node):

    def __init__(self,
                 id,
                 ip,
                 name,
                 status,
                 roles=None,
                 ssh_client=None,
                 info=None):
        super(DaisyNode, self).__init__(id, ip, name, status,
                                        roles, ssh_client, info)

    def is_odl(self):
        '''
        Returns if the node is an opendaylight
        '''
        if manager.Role.CONTROLLER in self.roles and self.is_active():
            cmd = 'docker inspect --format=\'{{.Name}}\' `docker ps -q`'
            output = self.run_cmd(cmd)
            if '/opendaylight' in output.rsplit('\n'):
                return True
        return False

    def get_ovs_info(self):
        '''
        Returns the ovs version installed
        '''
        if self.is_active():
            cmd = 'docker exec openvswitch_vswitchd ' \
                  'ovs-vsctl --version | head -1 | awk \'{print $NF}\''
            return self.run_cmd(cmd)
        return None
