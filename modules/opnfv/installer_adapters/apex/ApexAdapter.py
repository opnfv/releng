##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import os
import re

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

    def get_nodes(self):
        nodes = []
        output = self.runcmd_apex_installer(
            "source /home/stack/stackrc;nova list")
        lines = output.rsplit('\n')
        if len(lines) < 4:
            self.logger.info("No nodes found in the deployment.")
            return None

        for line in lines:
            if 'controller' in line:
                roles = "controller"
            elif 'compute' in line:
                roles = "compute"
            else:
                continue
            if 'Daylight' in line:
                roles = + ", OpenDaylight"
            fields = line.split('|')
            dict = {"id": re.sub('[!| ]', '', fields[1]),
                    "roles": roles,
                    "name": re.sub('[!| ]', '', fields[2]),
                    "status": re.sub('[!| ]', '', fields[3]),
                    "ip": re.sub('[!| ctlplane=]', '', fields[6])}
            nodes.append(dict)

        return nodes

    def get_deployment_info(self):
        str = "Deployment details:\n"
        str += "\tINSTALLER:   Apex\n"
        str += ("\tSCENARIO:    %s\n" %
                os.getenv('DEPLOY_SCENARIO', 'Unknown'))
        sdn = "None"

        nodes = self.get_nodes()
        if nodes is None:
            self.logger.info("No nodes found in the deployment.")
            return
        num_nodes = len(nodes)
        num_controllers = 0
        num_computes = 0
        for node in nodes:
            if 'controller' in node['roles']:
                num_controllers += 1
            if 'compute' in node['roles']:
                num_computes += 1
            if 'Daylight' in node['name']:
                sdn = 'OpenDaylight'

        ha = str(num_controllers >= 3)

        str += "\tHA:          %s\n" % ha
        str += "\tNUM.NODES:   %s\n" % num_nodes
        str += "\tCONTROLLERS: %s\n" % num_controllers
        str += "\tCOMPUTES:    %s\n" % num_computes
        str += "\tSDN CONTR.:  %s\n\n" % sdn

        str += "\tNODES:\n"
        for node in nodes:
            str += ("\t  ID:     %s\n" % node['id'])
            str += ("\t  Name:   %s\n" % node['name'])
            str += ("\t  Roles:  %s\n" % node['roles'])
            str += ("\t  Status: %s\n" % node['status'])
            str += ("\t  IP:     %s\n\n" % node['ip'])

        return str

    def get_controller_ips(self, options=None):
        nodes = self.get_nodes()
        controllers = []
        for node in nodes:
            if "controller" in node["roles"]:
                controllers.append(node['ip'])
        return controllers

    def get_compute_ips(self, options=None):
        nodes = self.get_nodes()
        computes = []
        for node in nodes:
            if "compute" in node["roles"]:
                computes.append(node['ip'])
        return computes

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

    def get_file_from_controller(self,
                                 remote_path,
                                 local_path,
                                 ip=None,
                                 options=None):
        if ip is None:
            controllers = self.get_controller_ips()
            ip = controllers[0]

        connection = ssh_utils.get_ssh_client(ip,
                                              'heat-admin',
                                              pkey_file=self.pkey_file)

        get_file_result = ssh_utils.get_file(connection,
                                             remote_path,
                                             local_path)
        if get_file_result is None:
            self.logger.error("SFTP failed to retrieve the file.")
            return 1
        self.logger.info("%s successfully copied from %s to %s" %
                         (remote_path, ip, local_path))
