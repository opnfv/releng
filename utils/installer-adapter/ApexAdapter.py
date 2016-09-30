##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


from SSHUtils import SSH_Connection


class ApexAdapter:

    def __init__(self, installer_ip):
        self.installer_ip = installer_ip

    def get_deployment_info(self):
        pass

    def get_nodes(self):
        pass

    def get_controller_ips(self):
        pass

    def get_compute_ips(self):
        pass

    def get_file_from_installer(self, origin, target, options=None):
        pass

    def get_file_from_controller(self, origin, target, ip=None, options=None):
        pass