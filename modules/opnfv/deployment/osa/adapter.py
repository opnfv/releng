##############################################################################
# Copyright (c) 2017 SUSE Linux GmbH
# Author: Manuel Buil (mbuil@suse.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


from opnfv.deployment import manager
from opnfv.utils import opnfv_logger as logger
from opnfv.utils import ssh_utils
import yaml

logger = logger.Logger(__name__).getLogger()


class OSAAdapter(manager.DeploymentHandler):

    def __init__(self, installer_ip, installer_user, pkey_file):
        self.SOURCE_PATH_UC = "/etc/openstack_deploy/openstack_hostnames_ips.yml"
        self.DEST_PATH_UC = "/tmp/openstack_user_config.yml"
        super(OSAAdapter, self).__init__(installer='osa',
                                         installer_ip=installer_ip,
                                         installer_user=installer_user,
                                         installer_pwd=None,
                                         pkey_file=pkey_file)

    def _find_nodes(self, file):
        nodes = []
        for line in file.keys():
            if "neutron_server_container" in line:
                nodes.append({line:file[line]})
            if "compute" in line:
                nodes.append({line:file[line]})
        return nodes

    def _process_nodes(self, raw_nodes):
        nodes = []

        for node in raw_nodes:
            name = node.keys()[0]
            ip = node[name]['container_address']
            # TODO when xci provides status and id of nodes add logic
            status = 'active'
            id = None
            if 'controller' in name:
                roles = 'controller'
            elif 'compute' in name:
                roles = 'compute'
            ssh_client = ssh_utils.get_ssh_client(hostname=ip,
                                                  username=self.installer_user,
                                                  pkey_file=self.pkey_file)
            node = manager.Node(id, ip, name, status, roles, ssh_client)
            nodes.append(node)

        return nodes

    def get_nodes(self, options=None):
        try:
            # if we have retrieved previously all the nodes, don't do it again
            # This fails the first time when the constructor calls this method
            # therefore the try/except
            if len(self.nodes) > 0:
                return self.nodes
        except:
            pass

        self.installer_node.get_file(self.SOURCE_PATH_UC, self.DEST_PATH_UC)
        with open(self.DEST_PATH_UC, 'r') as stream:
            try:
                file = yaml.load(stream)
                raw_nodes = self._find_nodes(file)
            except yaml.YAMLError as exc:
                logger.error(exc)
        nodes = self._process_nodes(raw_nodes)
        return nodes
