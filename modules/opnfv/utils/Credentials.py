#!/usr/bin/env python

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Usage example (note: Fuel actually uses key-based auth, not user/pass):
#   from opnfv.utils.Credentials import Credentials as credentials
#   credentials("fuel", "10.20.0.2", "user", "password").fetch('./openrc')
#

import os

import opnfv.installer_adapters.InstallerHandler as ins_handler
import opnfv.utils.Connection as con
import opnfv.utils.OPNFVLogger as logger


class Credentials(object):

    def __init__(self, installer, ip, user, password=None):
        self.installer = installer
        self.ip = ip
        self.logger = logger.Logger("Credentials", level="DEBUG").getLogger()
        self.connection = con.Connection()

        if self.__check_installer_name(self.installer) != os.EX_OK:
            self.logger.error("Installer %s not supported!" % self.installer)
            return os.EX_CONFIG
        else:
            self.logger.debug("Installer %s supported." % self.installer)

        if self.connection.verify_connectivity(self.ip) != os.EX_OK:
            self.logger.error("Installer %s not reachable!" % self.ip)
            return os.EX_UNAVAILABLE
        else:
            self.logger.debug("IP %s is reachable!" % self.ip)

        self.logger.debug(
            "Trying to stablish ssh connection to %s ..." % self.ip)
        self.handler = ins_handler.InstallerHandler(installer,
                                                    ip,
                                                    user,
                                                    password)

    def __check_installer_name(self, installer):
        if installer not in ("apex", "compass", "daisy", "fuel", "joid"):
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

    def __fetch_creds_apex(self, target_path):
        # TODO
        pass

    def __fetch_creds_compass(self, target_path):
        # TODO
        pass

    def __fetch_creds_daisy(self, target_path):
        # TODO
        pass

    def __fetch_creds_fuel(self, target_path):
        # TODO
        pass

    def __fetch_creds_joid(self, target_path):
        # TODO
        pass

    def fetch(self, target_path):
        if self.__check_path(target_path) != os.EX_OK:
            self.logger.error(
                "Target path %s does not exist!" % target_path)
            return os.EX_IOERR
        else:
            self.logger.debug("Target path correct.")

        self.logger.info("Fetching credentials from the deployment...")
        if self.installer == "apex":
            self.__fetch_creds_apex(target_path)
        elif self.installer == "compass":
            self.__fetch_creds_compass(target_path)
        elif self.installer == "daisy":
            self.__fetch_creds_daisy(target_path)
        elif self.installer == "fuel":
            self.__fetch_creds_fuel(target_path)
        elif self.installer == "joid":
            self.__fetch_creds_joid(target_path)
