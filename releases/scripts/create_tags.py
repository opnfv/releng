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
Create Gerrit Branchs
"""

import argparse

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

import logging
import os
import yaml

from requests.compat import quote
from requests.exceptions import RequestException

from pygerrit2.rest import GerritRestAPI
from pygerrit2.rest.auth import HTTPDigestAuthFromNetrc, HTTPBasicAuthFromNetrc


logging.basicConfig(level=logging.INFO)


def quote_branch(arguments):
    """
    Quote is used here to escape the '/' in branch name. By
    default '/' is listed in 'safe' characters which aren't escaped.
    quote is not used in the data of the PUT request, as quoting for
    arguments is handled by the request library
    """
    new_args = arguments.copy()
    new_args['branch'] = quote(new_args['branch'], '')
    return new_args


def create_tag(api, arguments):
    """
    Create a tag using the Gerrit REST API
    """
    logger = logging.getLogger(__file__)

    tag_data = """
    {
      "ref": "%(version)s"
      "revision": "%(commit)s"
    }""" % arguments

    # First verify the commit exists, otherwise the tag will be
    # created at HEAD
    try:
        request = api.get("/projects/%(project)s/commits/%(commit)s" %
                          arguments)
        logger.debug(request)
        logger.debug("Commit exists: %(commit)s", arguments)
    except RequestException as err:
        if hasattr(err, 'response') and err.response.status_code in [404]:
            logger.warn("Commit %(commit)s for %(project)s does"
                        " not exist.", arguments)
            logger.warn(err)
        else:
            logger.error("Error: %s", str(err))
        # Skip trying to create the branch
        return

    # Try to create the tag and let us know if it already exist.
    try:
        request = api.put("/projects/%(project)s/tags/%(version)s" %
                          quote_branch(arguments), tag_data)
        logger.info("Tag %(version)s for %(project)s successfully created",
                    arguments)
    except RequestException as err:
        if hasattr(err, 'response') and err.response.status_code in [412, 409]:
            logger.info("Tag %(version)s already created for %(project)s",
                        arguments)
            logger.info(err)
        else:
            logger.error("Error: %s", str(err))


def verify_tag(api, arguments):
    """
    Verify a tag exists in Gerrit and is on the correct branch
    """
    logger = logging.getLogger(__file__)

    tag_data = """
    {
      "ref": "%(version)s"
      "revision": "%(commit)s"
    }""" % arguments

    # First verify the commit exists, otherwise the tag will be
    # created at HEAD
    try:
        request = api.get("/projects/%(project)s/commits/%(commit)s" %
                          arguments)
        logger.debug(request)
        logger.debug("Commit exists: %(commit)s", arguments)
    except RequestException as err:
        if hasattr(err, 'response') and err.response.status_code in [404]:
            logger.warn("Commit %(commit)s for %(project)s does"
                        " not exist.", arguments)
            logger.warn(err)
        else:
            logger.error("Error: %s", str(err))

def verify_tags(restapi, project):
    """Verify tags in the release file exist and are on stable branch"""

    tags = []
    for item in project['releases']:
        repo, ref = next(iter(item['location'].items()))
        tags.append({
            'project': repo,
            'version': item['version'],
            'commit': ref
        })

    for tag in tags:
        verify_tag(restapi, tag)

def create_tags(restapi, project):
    """Create tags for a specific project defined in the release
    file"""

    tags = []
    for tag in project['releases']:
        repo, ref = next(iter(branch['location'].items()))
        branches.append({
            'project': repo,
            'version': branch['version'],
            'commit': ref
        })

    for tag in tags:
        create_tag(restapi, branch)


def main():
    """Given a yamlfile that follows the release syntax, create tags
    in Gerrit listed under releases"""

    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                'defaults.cfg'))
    config.read([os.path.expanduser('~/releases.cfg'), 'releases.cfg'])

    gerrit_url = config.get('gerrit', 'url')

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f',
                        type=argparse.FileType('r'),
                        required=True)
    parser.add_argument('--basicauth', '-b', action='store_true')
    parser.add_argument('--verify', '-v', action='store_true')
    args = parser.parse_args()

    GerritAuth = HTTPDigestAuthFromNetrc
    if args.basicauth:
        GerritAuth = HTTPBasicAuthFromNetrc

    try:
        auth = GerritAuth(url=gerrit_url)
    except ValueError as err:
        logging.error("%s for %s", err, gerrit_url)
        quit(1)
    restapi = GerritRestAPI(url=gerrit_url, auth=auth)

    project = yaml.safe_load(args.file)

    if args.verify:
        verify_tags(restapi, project)
    else:
        create_tags(restapi, project)


if __name__ == "__main__":
    main()
