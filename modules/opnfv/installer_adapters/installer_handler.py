##############################################################################
# Copyright (c) 2017 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os

from opnfv.utils import OPNFVLogger as logger


class InstallerHandler(object):

    EX_OK = os.EX_OK
    EX_ERROR = os.EX_SOFTWARE
    EX_INSTALLER_NOT_SUPPORTED = os.EX_SOFTWARE - 1
    EX_FUNCTION_NOT_IMPLEMENTED = os.EX_SOFTWARE - 2

    INSTALLERS = ["fuel", "apex", "compass", "joid", "daisy"]
    SDN_CONTROLLERS = ["opendaylight", "onos"]
    NODES = ['controller', 'compute']

    def __init__(self,
                 installer,
                 installer_ip,
                 installer_user,
                 installer_pwd=None,
                 private_key_file=None):

        self.installer = installer.lower()
        self.installer_ip = installer_ip
        self.installer_user = installer_user
        self.installer_pwd = installer_pwd
        self.private_key_file = private_key_file

        self.logger = logger.Logger("InstallerHandler").getLogger()

        if self.installer not in InstallerHandler.INSTALLERS:
            logger.error("Installer %s is  not supported. "
                         "Please use one of the following: %s"
                         % (self.installer, INSTALLERS))
            return InstallerHandler.EX_INSTALLER_NOT_SUPPORTED

    def _default(self):
        self.logger.error("Not implemented.")
        return InstallerHandler.EX_FUNCTION_NOT_IMPLEMENTED

    def get_deployment_info(self):
        return self._default()

    def get_nodes(self, options=None):
        return self._default()

    def get_controller_ips(self, options=None):
        return self._default()

    def get_compute_ips(self, options=None):
        return self._default()

    def get_file_from_installer(self,
                                remote_path,
                                local_path,
                                options=None):
        return self._default()

    def get_file_from_controller(self,
                                 remote_path,
                                 local_path,
                                 ip=None,
                                 options=None):
        return self._default()
