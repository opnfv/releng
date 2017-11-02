#!/usr/bin/python

##############################################################################
# Copyright (c) jalausuch@suse.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


import argparse
import os
import shutil
import sys
import yaml

from opnfv.utils import opnfv_logger as logger
from opnfv.utils import ssh_utils

logger = logger.Logger("LogCollector").getLogger()


class Node(object):
    def __init__(self,
                 name,
                 ip,
                 user,
                 private_key_file=None,
                 password=None,
                 log_paths=[]):
        self.name = name
        self.ip = ip
        self.user = user
        self.private_key_file = private_key_file
        self.password = password
        self.log_paths = log_paths

    def get_ssh_client(self):
        self.ssh_client = ssh_utils.get_ssh_client(
            hostname=self.ip,
            username=self.user,
            password=self.password,
            pkey_file=self.private_key_file)

    def get_paths(self):
        return self.log_paths

    def get_name(self):
        return self.name

    def __str__(self):
        return "name={}, ip={}, user={}, key={}, password={}, paths={}".format(
            self.name, self.ip, self.user,
            self.private_key_file, self.password, self.log_paths)


class LogCollector(object):
    def __init__(self,
                 nodes_file,
                 logs_local_dir='./opnfv_logs',
                 push_to_artifact=False):
        self.nodes_file = nodes_file
        self.logs_local_dir = logs_local_dir
        self.push_to_artifact = push_to_artifact
        if os.path.exists(self.logs_local_dir):
            logger.info('Removed previous local logs.')
            shutil.rmtree(self.logs_local_dir)
        os.makedirs(self.logs_local_dir)
        logger.info('Directory {} created'.format(self.logs_local_dir))

    def read_yaml(self):
        stream = open(self.nodes_file, "r")
        nodesyaml = yaml.load(stream)['nodes']
        nodes = []
        for n in nodesyaml:
            nodes.append(Node(
                name=n['name'],
                ip=n['ip'],
                user=n['user'],
                private_key_file=n['key_filename'],
                password=n['password'],
                log_paths=n['paths'],
                ))
            logger.info("Added node '{}'".format(n['name']))
        return nodes

    def get_dir(self):
        return self.logs_local_dir


def main(**kwargs):
    nodes_file = kwargs['nodes_file']
    if not os.path.isfile(nodes_file):
        logger.error("File {} does not exist.".format(nodes_file))
        return -1
    logcollector = LogCollector(nodes_file=nodes_file)
    nodes = logcollector.read_yaml()
    for node in nodes:
        ssh_conn = node.get_ssh_client()
        for path in node.log_paths:
            print path
            dest = (logcollector.get_dir() + '/' + node.get_name() + path)
            if ssh_utils.get_file(ssh_conn, path, dest):
                logger.info("Copied '{}'' from node '{}' to '{}'".format(
                    path, node.get_name(), dest))
            else:
                logger.error("Error copying '{}'' from node '{}' to "
                             "'{}'".format(path, node.get_name(), dest))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("nodes_file", type=str,
                        help="Yaml file with the information of the "
                        "nodes and paths to the logs to be fetched. ")
    args = vars(parser.parse_args(sys.argv[1:]))
    sys.exit(main(**args))
