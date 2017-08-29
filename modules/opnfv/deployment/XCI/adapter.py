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

logger = logger.Logger(__name__).getLogger()


class XCIAdapter(manager.DeploymentHandler):

    def __init__(self, installer_ip, installer_user, installer_pwd):
        super(FuelAdapter, self).__init__(installer='xci',
                                          installer_ip=installer_ip,
                                          installer_user=installer_user,
                                          installer_pwd=None,
                                          pkey_file=None)

    def _find_nodes(self)
        nodes = {}
        cmd = "cat /etc/openstack_deploy/openstack_user_config.yml | grep "
        for i in range(0,9):
            controller_item = "controller0" + str(i)
            cmd_controller = cmd + controller_item
            output1 = self.installer_node.run_cmd(cmd_controller)
            if output1:
                ip = _find_ip(controller_item)
                nodes[controller_item] = ip
            compute_item - "compute0" + str(i)
            cmd_compute = cmd + compute_item
            output2 = self.installer_node.run_cmd(cmd_compute)
            if output2:
                ip = _find_ip(compute_item)
                nodes[compute_item] = ip

            if (not output1 and not output2):
                break
       
        return nodes

    def _find_ip(self, host):
        cmd = "cat /etc/openstack_deploy/openstack_user_config.yml | grep " + host + " -n1 | grep ip | cut -d: -f2"
        output = self.installer_node.run_cmd(cmd)        
        return output.lstrip()

    def get_nodes(self, options=None):
        nodes = _find_nodes()
