##############################################################################
# Copyright (c) 2018 Tim Rozet (trozet@redhat.com) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import argparse
import sys
import yaml


def get_node_data_by_number(node_type, node_number):
    node_idx = 1
    for node_name, node_data in data['servers'].items():
        if node_type == node_data['type']:
            if node_idx == node_number:
                return node_name, node_data
            else:
                node_idx += 1


def get_node_value(node_type, node_number, key):
    node_name, node_data = get_node_data_by_number(node_type, node_number)
    if not key and node_name is not None:
        return node_name
    elif node_data and isinstance(node_data, dict) and key in node_data:
        return node_data[key]


def get_number_of_nodes(node_type):
    nodes = data['servers']
    num_nodes = 0
    for node_name, node_data in nodes.items():
        if node_data['type'] == node_type:
            num_nodes += 1
    return num_nodes


FUNCTION_MAP = {'num_nodes':
                {'func': get_number_of_nodes,
                 'args': ['node_type']},
                'get_value':
                    {'func': get_node_value,
                     'args': ['node_type', 'node_number', 'key']},
                }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=FUNCTION_MAP.keys())
    parser.add_argument('-f', '--file',
                        dest='node_file',
                        required=True)
    parser.add_argument('--node-type',
                        default='controller',
                        required=False)
    parser.add_argument('--node-number',
                        default=1,
                        type=int,
                        required=False)
    parser.add_argument('-k', '--key',
                        required=False)
    args = parser.parse_args(sys.argv[1:])
    with open(args.node_file, 'r') as fh:
        data = yaml.safe_load(fh)
    assert 'servers' in data
    func = FUNCTION_MAP[args.command]['func']
    args = [getattr(args, x) for x in FUNCTION_MAP[args.command]['args']]
    print(func(*args))
