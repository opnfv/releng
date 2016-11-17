##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


import opnfv.utils.SSHUtils as ssh_utils
import opnfv.utils.OPNFVLogger as logger


class ApexAdapter:

    def __init__(self, installer_ip, pkey_file, user="stack"):
        self.installer_ip = installer_ip
        self.installer_user = user
        self.pkey_file = pkey_file
        self.installer_connection = ssh_utils.get_ssh_client(
            self.installer_ip,
            self.installer_user,
            pkey_file=self.pkey_file)
        self.logger = logger.Logger("ApexHandler").getLogger()

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
            "source /home/stack/stackrc;nova list")
        # self.logger(output)
        dir(output)
        type(output)
        print output

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
