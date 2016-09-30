##############################################################################
# Copyright (c) 2015 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from FuelAdapter import FuelAdapter
from ApexAdapter import ApexAdapter
from CompassAdapter import CompassAdapter
from JoidAdapter import JoidAdapter


INSTALLERS = ["fuel", "apex", "compass", "joid"]


class InstallerHandler:

    def __init__(self,
                 scenario,
                 installer,
                 installer_ip,
                 installer_user,
                 installer_pwd=None):
        self.scenario = scenario
        self.installer = installer.lower()
        self.installer_ip = installer_ip
        self.installer_user = installer_user
        self.installer_pwd = installer_pwd

        if self.installer == INSTALLERS[0]:
            self.InstallerAdapter = FuelAdapter(self.installer_ip,
                                                self.installer_user,
                                                self.installer_pwd)
        elif self.installer == INSTALLERS[1]:
            self.InstallerAdapter = ApexAdapter(self.installer_ip)
        elif self.installer == INSTALLERS[2]:
            self.InstallerAdapter = CompassAdapter(self.installer_ip)
        elif self.installer == INSTALLERS[3]:
            self.InstallerAdapter = JoidAdapter(self.installer_ip)
        else:
            print("Installer %s is  not valid. "
                  "Please use one of the followings: %s"
                  % (self.installer, INSTALLERS))
            exit(1)

    def get_deployment_info(self):
        return self.InstallerAdapter.get_deployment_info()

    def get_nodes(self):
        return self.InstallerAdapter.get_nodes()

    def get_controller_ips(self):
        return self.InstallerAdapter.get_controller_ips()

    def get_compute_ips(self):
        return self.InstallerAdapter.get_compute_ips()

    def get_all(self):
        pass
