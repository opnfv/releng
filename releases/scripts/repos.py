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
    args = parser.parse_args()

    project = yaml.safe_load(args.file)

    list_repos(project, args)


def list_repos(project, args):
    """List repositories in the project file"""

    repos = []
    if not 'releases' in project:
        lookup = project['branches']
    else:
        lookup = project['releases']
    for branch in lookup:
        repo, ref = next(iter(branch['location'].items()))
        if args.names:
            print(repo)
        else:
            if not 'releases' in project:
                print("%s" % repo)
            else:
                print("%s: %s" % (repo, ref))


if __name__ == "__main__":
    main()
