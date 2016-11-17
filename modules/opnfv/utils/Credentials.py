
# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

import os

import opnfv.utils.Connection as con
from opnfv.installer_adapters.InstallerHandler import InstallerHandler
import opnfv.utils.OPNFVLogger as logger


class Credentials(object):

    def __init__(self, installer, ip, target_path, user, password=None):
        self.installer = installer
        self.ip = ip
        self.target_path = target_path
        self.logger = logger.Logger("Credentials", level="DEBUG").getLogger()
        self.connection = con.Connection()

        if self.__check_installer_name(self.installer) != os.EX_OK:
            self.logger.error("Installer %s not supported!" % self.installer)
            return os.EX_CONFIG
        else:
            self.logger.debug("Installer %s supported." % self.installer)

        if self.__check_path(self.target_path) != os.EX_OK:
            self.logger.error(
                "Target path %s does not exist!" % self.target_path)
            return os.EX_IOERR
        else:
            self.logger.debug("Target path correct.")

        if self.connection.verify_connectivity(self.ip) != os.EX_OK:
            self.logger.error("Installer %s not reachable!" % self.ip)
            return os.EX_UNAVAILABLE
        else:
            self.logger.debug("IP %s is reachable!" % self.ip)

        self.logger.debug(
            "Trying to stablish ssh connection to %s ..." % self.ip)
        self.installer = InstallerHandler(installer,
                                          ip,
                                          user,
                                          password)

    def __check_installer_name(self, installer):
        if installer not in ("apex", "compass", "fuel", "joid"):
            return os.EX_CONFIG
        else:
            return os.EX_OK

    def __check_path(self, path):
        try:
            with open(path, 'a'):
                os.utime(path, None)
            return os.EX_OK
        except IOError as e:
            self.logger.error(e)
            return os.EX_IOERR

    def __fetch_creds_apex(self):
        # TODO
        pass

    def __fetch_creds_compass(self):
        # TODO
        pass

    def __fetch_creds_fuel(self):
        # TODO
        pass

    def __fetch_creds_joid(self):
        # TODO
        pass

    def fetch(self):
        logger.error("Fetching credentials from the deployment...")
        if self.installer == "apex":
            self.__fetch_creds_apex()
        elif self.installer == "compass":
            self.__fetch_creds_compass()
        elif self.installer == "fuel":
            self.__fetch_creds_fuel()
        elif self.installer == "joid":
            self.__fetch_creds_joid()
