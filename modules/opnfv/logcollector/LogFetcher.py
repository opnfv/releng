##############################################################################
# Copyright (c) 2017 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os
import sys
import yaml

from opnfv.deployment import factory


class LogFetcher:

    def __init__(self,
                 installer,
                 installer_ip,
                 installer_user,
                 installer_pwd=None,
                 pkey_file=None,
                 logs_dir='./installer_logs'):

        self.installer = installer
        self.logs_dir = logs_dir
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        try:
            self.handler = factory.Factory.get_handler(
                installer=installer,
                installer_ip=installer_ip,
                installer_user=installer_user,
                installer_pwd=password,
                pkey_file=pkey_file)

            self.nodes = handler.get_nodes()
        except:
            logger.error("Cannot create deployment handler.")
            exit(1)

    def fetch_file_from_controller(self, remote_path, local_path):
        file_path = os.path.dirname(remote_path)
        #file_name = os.path.basename(remote_path)
        abs_local_path = local_path + file_path
        if not os.path.exists(abs_local_path):
            os.makedirs(abs_local_path)

        for node in self.nodes:
            if node.is_controller():
                try:
                    logger.info("Fetching %s from controller %s" %
                                (remote_path, node.ip))
                    node.get_file(remote_path, local_path)
                except:
                    logger.error("Problem to fetch %s from %s" %
                                 (remote_path, node.ip))

    def fetch_all_logs(self):
        # Read yaml file
        this_path = os.path.dirname(sys.argv[0])
        full_path = os.path.abspath(this_path)
        list_file = os.path.join(full_path, 'files.yaml')
        stream = open(list_file, "r")
        yamllist = yaml.load(stream)

        # Fetch common files
        common_controller = yamllist['common']['controller']
        controller_log_path = os.path.join(self.logs_dir, 'controller')

        for file in common_controller:
            self.fetch_file_from_controller(file, controller_log_path)

        # Fetch specific files
        installer_controller = yamllist[self.installer]['controller']
        for file in installer_controller:
            self.fetch_file_from_controller(file, controller_log_path)
