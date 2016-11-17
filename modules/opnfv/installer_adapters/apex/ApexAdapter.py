##############################################################################
# Copyright (c) 2017 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


import re
import subprocess

import opnfv.modules.utils.SSHUtils as ssh_utils
import opnfv.modules.utils.OPNFVLogger as logger


class ApexAdapter:

    def __init__(self, user="stack", installer_ip):
        self.logger = logger.Logger("ApexHandler").getLogger()
        self.installer_ip = installer_ip
        self.installer_user = user
        self.installer_connection = ssh_utils.get_ssh_client(
            self.installer_ip,
            self.installer_user)

    def runcmd_apex_installer(self, cmd):
        _, stdout, stderr = (self.installer_connection.exec_command(cmd))
        error = stderr.readlines()
        if len(error) > 0:
            self.logger.error("error %s" % ''.join(error))
            return error
        output = ''.join(stdout.readlines())
        return output

    def get_deployment_info(self):
        output = self.runcmd_apex_installer(
            "source /home/stack/overcloudrc;nova list")
        self.logger(output)

    def get_nodes(self):
        pass

    def get_controller_ips(self):
        pass

    def get_compute_ips(self):
        pass

    def get_file_from_installer(self, remote_path, local_path, options=None):
        self.logger.debug("Fetching %s from Undercloud %s" %
                          (remote_path, self.installer_ip))
        get_file_result = ssh_utils.get_file(self.installer_connection,
                                             remote_path,
                                             local_path)
        if get_file_result is None:
            self.logger.error("SFTP failed to retrieve the file.")
            return 1
        self.logger.info("%s successfully copied from Undercloud to %s" %
                         (remote_path, local_path))

    def get_file_from_controller(self, origin, target, ip=None, options=None):
        pass
