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

    def __init__(self, installer_ip, installer_user):
        super(OSAAdapter, self).__init__(installer='osa',
                                          installer_ip=installer_ip,
                                          installer_user=installer_user,
                                          installer_pwd=None,
                                          pkey_file=None)

    def _find_nodes(self, file):
        nodes = file['compute_hosts']
        controllers = file['haproxy_hosts']
        return nodes

    def get_nodes(self, options=None):
        output = self.installer_node.run_cmd("ls /etc/openstack_deploy/")
        self.installer_node.get_file("/etc/openstack_deploy/openstack_user_config.yml", "/tmp/openstack_user_config.yml")
        with open("/tmp/openstack_user_config.yml", 'r') as stream:
            try:
                file = yaml.load(stream)
                nodes = self._find_nodes(file)
            except yaml.YAMLError as exc:
                print(exc)
