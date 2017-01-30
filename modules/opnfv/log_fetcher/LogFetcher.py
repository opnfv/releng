##############################################################################
# Copyright (c) 2017 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os
import yaml

import opnfv.installer_adapters.InstallerHandler as ins_handler


class LogFetcher:

    def __init__(self,
                 installer,
                 installer_ip,
                 installer_user,
                 installer_pwd=None,
                 private_key_file=None,
                 logs_dir='./installer_logs'):

        self.installer = installer
        self.logs_dir = logs_dir
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        self.handler = ins_handler.InstallerHandler(
            installer=installer,
            installer_ip=installer_ip,
            installer_user=installer_user,
            installer_pwd=installer_pwd,
            private_key_file=private_key_file)

    def fetch_file_from_controller(self, remote_path, local_path):
        handler.get_file_from_controller(remote_path, local_path)

    def fetch_all_logs(self):
        stream = open("files.yaml", "r")
        yaml = yaml.load(stream)

        # Fetch common files
        common_controller = yaml['common']['controller']
        controller_log_path = os.path.join(self.logs_dir, 'controller')
        os.makedirs(controller_log_path)
        for file in common_controller:
            self.fetch_file_from_controller(file, controller_log_path)

        # Fetch specific files
        installer_controller = yaml[self.installer]['controller']
        for file in installer_controller:
            self.fetch_file_from_controller(file, controller_log_path)
