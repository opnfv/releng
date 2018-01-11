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
Create Gerrit Branches
"""

import argparse
import logging
import os
import re
import yaml

from ruamel.yaml import YAML


logging.basicConfig(level=logging.INFO)


def has_string(filepath, string):
    """
    Return True if the given filepath contains the regex string
    """
    with open(filepath) as yaml_file:
        for line in yaml_file:
            if string.search(line):
                return True
    return False


def jjb_files(project, release):
    """
    Return sets of YAML file names that contain 'stream' for a given
    project, and file that already contain the stream.
    """
    files, skipped = set(), set()
    file_ending = re.compile(r'ya?ml$')
    search_string = re.compile(r'^\s+stream:')
    release_string = re.compile(r'- %s:' % release)
    jjb_path = os.path.join('jjb', project)

    for file_name in os.listdir(jjb_path):
        file_path = os.path.join(jjb_path, file_name)
        if file_ending.search(file_path) and os.path.isfile(file_path):
            if has_string(file_path, release_string):
                skipped.add(file_path)
            elif has_string(file_path, search_string):
                files.add(file_path)
    return (files, skipped)


def main():
    """
    Create Jenkins Jobs for stable branches in Release File
    """
    logger = logging.getLogger()

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f',
                        type=argparse.FileType('r'),
                        required=True)
    args = parser.parse_args()

    project = yaml.safe_load(args.file)

    # Get the release name from the file path
    release = os.path.split(os.path.dirname(args.file.name))[1]

    # TODO: Create branch jobs for each branch? Does that even make sense when
    #   we only have one stable branch per-release?
    arg = {
        'project': project['branches'][0]['repo'],
        'branch': project['branches'][0]['name'],
    }

    yaml_parser = YAML()
    yaml_parser.preserve_quotes = True
    yaml_parser.explicit_start = True

    (job_files, skipped_files) = jjb_files(arg['project'], release)

    logger.info("Jobs already exists for %s in files: %s",
                arg['project'], ', '.join(skipped_files))
    # Exit if there are not jobs to create
    if not job_files:
        return
    logger.info("Creating Jenkins Jobs for %s in files: %s",
                arg['project'], ', '.join(job_files))

    stable_branch_stream = """\
      %s:
          branch: 'stable/{stream}'
          gs-pathname: '/{stream}'
          disabled: false
    """ % release

    stable_branch_yaml = yaml_parser.safe_load(stable_branch_stream)
    stable_branch_yaml[release].yaml_set_anchor(release, always_dump=True)

    for job_file in job_files:
        yaml_jjb = yaml_parser.safe_load(open(job_file))

        project_config = yaml_jjb[0]['project']['stream']
        # There is an odd issue where just appending adds a newline before the
        # branch config, so we append (presumably after master) instead.
        project_config.insert(1, stable_branch_yaml)

        # TODO: Fix indentation so only sublists are indented by 2
        #   as currently this is modifying almost every line of the file
        #   http://yaml.readthedocs.io/en/latest/example.html
        #   https://stackoverflow.com/questions/48029461/ \
        #      how-to-preserve-indenting-in-key-value-when-dumping-yaml
        yaml_parser.dump(yaml_jjb, open(job_file, 'w'))


if __name__ == "__main__":
    main()
