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
import subprocess

# import ruamel
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

    if not os.path.isdir(jjb_path):
        logging.warn("JJB directory does not exist at %s, skipping job "
                     "creation", jjb_path)
        return (files, skipped)

    for file_name in os.listdir(jjb_path):
        file_path = os.path.join(jjb_path, file_name)
        if os.path.isfile(file_path) and file_ending.search(file_path):
            if has_string(file_path, release_string):
                skipped.add(file_path)
            elif has_string(file_path, search_string):
                files.add(file_path)
    return (files, skipped)


def main():
    """
    Create Jenkins Jobs for stable branches in Release File
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f',
                        type=argparse.FileType('r'),
                        required=True)
    args = parser.parse_args()

    project_yaml = yaml.safe_load(args.file)

    # Get the release name from the file path
    release = os.path.split(os.path.dirname(args.file.name))[1]

    create_jobs(release, project_yaml)


def create_jobs(release, project_yaml):
    """Add YAML to JJB files for release stream"""
    logger = logging.getLogger(__file__)

    # We assume here project keep their subrepo jobs under the part
    # project name. Otherwise we'll have to look for jjb/<repo> for each
    # branch listed.
    project, _ = next(iter(project_yaml['branches'][0]['location'].items()))

    yaml_parser = YAML()
    yaml_parser.preserve_quotes = True
    yaml_parser.explicit_start = True
    # yaml_parser.indent(mapping=4, sequence=0, offset=0)
    # These are some esoteric values that produce indentation matching our jjb
    # configs
    # yaml_parser.indent(mapping=3, sequence=3, offset=2)
    # yaml_parser.indent(sequence=4, offset=2)
    yaml_parser.indent(mapping=2, sequence=4, offset=2)

    (job_files, skipped_files) = jjb_files(project, release)

    if skipped_files:
        logger.info("Jobs already exists for %s in files: %s",
                    project, ', '.join(skipped_files))
    # Exit if there are not jobs to create
    if not job_files:
        return
    logger.info("Creating Jenkins Jobs for %s in files: %s",
                project, ', '.join(job_files))

    stable_branch_stream = """\
      %s:
          branch: 'stable/{stream}'
          gs-pathname: '/{stream}'
          disabled: false
    """ % release

    stable_branch_yaml = yaml_parser.load(stable_branch_stream)
    stable_branch_yaml[release].yaml_set_anchor(release, always_dump=True)

    for job_file in job_files:
        yaml_jjb = yaml_parser.load(open(job_file))
        if 'stream' not in yaml_jjb[0]['project']:
            continue

        # TODO: Some JJB files don't have 'stream'
        project_config = yaml_jjb[0]['project']['stream']
        # There is an odd issue where just appending adds a newline before the
        # branch config, so we append (presumably after master) instead.
        project_config.insert(1, stable_branch_yaml)

        # NOTE: In the future, we may need to override one or multiple of the
        #       following ruamal Emitter methods:
        #         * ruamel.yaml.emitter.Emitter.expect_block_sequence_item
        #         * ruamel.yaml.emitter.Emitter.write_indent
        #       To hopefully replace the need to shell out to sed...
        yaml_parser.dump(yaml_jjb, open(job_file, 'w'))
        args = ['sed', '-i', 's/^  //', job_file]
        subprocess.Popen(args, stdout=subprocess.PIPE, shell=False)


if __name__ == "__main__":
    main()
