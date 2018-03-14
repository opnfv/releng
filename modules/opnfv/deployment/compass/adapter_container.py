#!/usr/bin/env python

# Copyright (c) 2018 HUAWEI TECHNOLOGIES CO.,LTD and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

from opnfv.deployment import manager
from opnfv.utils import opnfv_logger as logger
from opnfv.utils import ssh_utils

import yaml
import os

logger = logger.Logger(__name__).getLogger()


class ContainerizedCompassAdapter():

    def __init__(self, installer_ip, installer_user, pkey_file):

        self.installer = 'compass'
        self.installer_ip = installer_ip
        self.installer_user = installer_user
        self.pkey_file = pkey_file
        self.DST_PATH_UC = "/tmp/openstack_user_config.yml"
        self.nodes = []
        self.ROLES = {}

        if pkey_file is not None and not os.path.isfile(pkey_file):
            raise Exception(
                'The private key file %s does not exist!' % pkey_file)

    def _find_nodes(self, file):
        nodes = file['compute_hosts']
        for compute in nodes:
            self.ROLES[compute] = 'compute'
        controllers = file['haproxy_hosts']
        for controller in controllers:
            nodes[controller] = controllers[controller]
            self.ROLES[controller] = 'controller'
        return nodes

    def _process_nodes(self, raw_nodes):
        nodes = []

        for node in raw_nodes:
            name = node
            ip = raw_nodes[node]['ip']
            status = 'active'
            id = None
            if self.ROLES[node] == 'controller':
                roles = 'controller'
            elif self.ROLES[node] == 'compute':
                roles = 'compute'
            ssh_client = ssh_utils.get_ssh_client(hostname=ip,
                                                  username=self.installer_user,
                                                  pkey_file=self.pkey_file)
            node = manager.Node(id, ip, name, status, roles, ssh_client)
            nodes.append(node)

        return nodes

    def get_nodes(self, options=None):
        try:
            # if we have retrieved previously all the nodes, don't do it again
            # This fails the first time when the constructor calls this method
            # therefore the try/except
            if len(self.nodes) > 0:
                return self.nodes
        except:
            pass

        with open(self.DST_PATH_UC, 'r') as stream:
            try:
                file = yaml.load(stream)
                raw_nodes = self._find_nodes(file)
            except yaml.YAMLError as exc:
                logger.error(exc)
        self.nodes = self._process_nodes(raw_nodes)
        return self.nodes
