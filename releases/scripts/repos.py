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
import yaml


def main():
    """Given a release yamlfile list the repos it contains"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f',
                        type=argparse.FileType('r'),
                        required=True)
    parser.add_argument('--names', '-n',
                        action='store_true',
                        default=False,
                        help="Only print the names of repos, "
                             "not their SHAs")
    parser.add_argument('--release', '-r',
                        type=str,
                        help="Only print"
                             "SHAs for the specified release")
    args = parser.parse_args()

    project = yaml.safe_load(args.file)

    list_repos(project, args)


def list_repos(project, args):
    """List repositories in the project file"""

    lookup = project.get('releases', [])
    if 'releases' not in project:
        exit(0)

    for item in lookup:
        repo, ref = next(iter(item['location'].items()))
        if args.names:
            print(repo)
        elif args.release and item['version'] == args.release:
            print("%s %s" % (repo, ref))
        elif not args.release:
            # Print all releases
            print("%s %s %s" % (repo, item['version'], ref))


if __name__ == "__main__":
    main()
