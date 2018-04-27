#!/usr/bin/env python2
# SPDX-License-Identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
"""
List Release Repos
"""

import argparse

import os
import yaml


def main():
    """Given a release yamlfile list the repos it contains"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f',
                        type=argparse.FileType('r'),
                        required=True)
    parser.add_argument('--names', '-n', action='store_true')
    parser.add_argument('--release', '-r', type=str)
    args = parser.parse_args()

    project = yaml.safe_load(args.file)

    list_repos(project, args)


def list_repos(project, args):
    """List repositories in the project file"""

    repos = []
    if args.names:
        if 'releases' not in project:
            lookup = project['branches']
        else:
            lookup = project['releases']
    elif args.release:
        if 'releases' not in project:
            exit(0)
        lookup = project['releases']
    for item in lookup:
        repo, ref = next(iter(item['location'].items()))
        if args.names:
            print(repo)
        elif args.release:
            if item['version'] == args.release:
                print("%s %s" % (repo, ref))
        elif False:
            if not 'releases' in project:
                print("%s" % repo)
            else:
                print("%s: %s" % (repo, ref))


if __name__ == "__main__":
    main()
