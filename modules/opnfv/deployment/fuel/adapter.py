##############################################################################
# Copyright (c) 2018 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
#         George Paraskevopoulos (geopar@intracom-telecom.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
'''
    This modules implements the Fuel@OPNFV adapter

    - host executing this module needs network connectivity to a cluster via:
      * mcpcontrol network (usually 10.20.0.0/24, created by installer);
      * PXE/admin network;
      The above are always true for an OPNFV Pharos jumpserver.
    - key-based SSH auth is used throughout the cluster, without proxy-ing
      cluster node access via Salt master (old Fuel@OPNFV used to);
'''

from yaml import safe_load, YAMLError

from opnfv.deployment import manager
from opnfv.utils import opnfv_logger as logger
from opnfv.utils import ssh_utils

LOGGER = logger.Logger(__name__).getLogger()


class FuelAdapter(manager.DeploymentHandler):
    '''
        This class extends the generic handler with Fuel@OPNFV specifics
    '''

    def __init__(self, installer_ip, installer_user, pkey_file):
        super(FuelAdapter, self).__init__(installer='fuel',
                                          installer_ip=installer_ip,
                                          installer_user=installer_user,
                                          installer_pwd=None,
                                          pkey_file=pkey_file)

    def get_nodes(self, options=None):
        '''
            Generates a list of all the nodes in the deployment
        '''
        # Unlike old Fuel@Openstack, we don't keep track of different clusters
        # explicitly, but through domain names.
        # For simplicity, we will assume a single cluster per Salt master node.
        try:
            # if we have retrieved previously all the nodes, don't do it again
            # This fails the first time when the constructor calls this method
            # therefore the try/except
            if len(self.nodes) > 0:
                return self.nodes
        # pylint: disable=bare-except
        except:
            pass

        # Manager roles to reclass properties mapping
        _map = {
            'salt:master:enabled': manager.Role.INSTALLER,
            'maas:region:enabled': manager.Role.INSTALLER,
            'nova:controller:enabled': manager.Role.CONTROLLER,
            'nova:compute:enabled': manager.Role.COMPUTE,
            'opendaylight:server:enabled': manager.Role.ODL,
            'onos:server:enabled': manager.Role.ONOS
        }
        nodes = []
        cmd = ("sudo salt '*' pillar.item {} --out yaml --static 2>/dev/null"
               .format(' '.join(_map.keys() + ['_param:pxe_admin_address'])))
        # Sample output (for one node):
        #   cmp001.mcp-ovs-noha.local:
        #     _param:pxe_admin_address: 192.168.11.34
        #     maas:region:enabled: ''
        #     nova:compute:enabled: true
        #     nova:controller:enabled: ''
        #     opendaylight:server:enabled: ''
        #     retcode: 0
        #     salt:master:enabled: ''
        output = self.installer_node.run_cmd(cmd)
        if output.startswith('No minions matched the target'):
            LOGGER.info('No nodes found in the deployment.')
            return nodes

        try:
            yaml_output = safe_load(output)
        except YAMLError as exc:
            LOGGER.error(exc)
        for node_name in yaml_output.keys():
            ip_addr = yaml_output[node_name]['_param:pxe_admin_address']
            ssh_client = ssh_utils.get_ssh_client(hostname=ip_addr,
                                                  username='ubuntu',
                                                  pkey_file=self.pkey_file)
            node = manager.Node(
                id=node_name,
                ip=ip_addr,
                name=node_name,
                status=manager.NodeStatus.STATUS_OK,
                roles=[_map[x] for x in _map if yaml_output[node_name][x]],
                ssh_client=ssh_client)
            nodes.append(node)

        return nodes

    def get_openstack_version(self):
        '''
        Returns a string of the openstack version (nova-compute)
        '''
        cmd = ("sudo salt -C 'I@nova:controller and *01*' "
               "cmd.run 'nova-manage version 2>/dev/null' --out yaml --static")
        nova_version = self.installer_node.run_cmd(cmd)
        if nova_version:
            return nova_version.split(' ')[-1]
        return None

    def get_sdn_version(self):
        '''
        Returns a string of the sdn controller and its version, if exists
        '''
        cmd = ("sudo salt -C 'I@opendaylight:server and *01*'"
               "pkg.version opendaylight --out yaml --static")
        version = None
        for node in self.nodes:
            if manager.Role.ODL in node.roles and node.is_active():
                odl_version = self.installer_node.run_cmd(cmd)
                if odl_version:
                    version = 'OpenDaylight ' + odl_version.split(' ')[-1]
                    break
        return version

    def get_deployment_status(self):
        '''
        Returns a string of the status of the deployment
        '''
        # NOTE: Requires Fuel-side signaling of deployment status, stub it
        return 'active'
