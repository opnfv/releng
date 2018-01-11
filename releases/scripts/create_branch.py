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
import ConfigParser
import logging
import os
import yaml

from requests.compat import quote
from requests.exceptions import RequestException

from pygerrit2.rest import GerritRestAPI
from pygerrit2.rest.auth import HTTPBasicAuthFromNetrc


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


def create_branch(api, arguments):
    """
    Create a branch using the Gerrit REST API
    """
    logger = logging.getLogger()

    branch_data = """
    {
      "ref": "%(branch)s"
      "revision": "%(commit)s"
    }""" % arguments

    # First verify the commit exists, otherwise the branch will be
    # created at HEAD
    try:
        request = api.get("/projects/%(project)s/commits/%(commit)s" %
                          arguments)
        logger.debug(request)
        logger.debug("Commit exists: %(commit)s", arguments)
    except RequestException as err:
        if err.response.status_code in [404]:
            logger.warn("Commit %(commit)s for %(project)s:%(branch)s does"
                        " not exist. Not creating branch.", arguments)
        else:
            logger.error("Error: %s", str(err))
        # Skip trying to create the branch
        return

    # Try to create the branch and let us know if it already exist.
    try:
        request = api.put("/projects/%(project)s/branches/%(branch)s" %
                          quote_branch(arguments), branch_data)
        logger.info("Branch %(branch)s for %(project)s successfully created",
                    arguments)
    except RequestException as err:
        if err.response.status_code in [412, 409]:
            logger.info("Branch %(branch)s already created for %(project)s",
                        arguments)
        else:
            logger.error("Error: %s", str(err))


def main():
    """Given a yamlfile that follows the release syntax, create branches
    in Gerrit listed under branches"""

    config = ConfigParser.ConfigParser()
    config.read('defaults.cfg')
    config.read([os.path.expanduser('~/releases.cfg'), 'releases.cfg'])

    gerrit_url = config.get('gerrit', 'url')

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f',
                        type=argparse.FileType('r'),
                        required=True)
    args = parser.parse_args()

    try:
        auth = HTTPBasicAuthFromNetrc(url=gerrit_url)
    except ValueError, err:
        logging.error("%s for %s", err, gerrit_url)
        quit(1)
    restapi = GerritRestAPI(url=gerrit_url, auth=auth)

    project = yaml.load(args.file)

    create_branches(restapi, project)


def create_branches(restapi, project):
    """Create branches for a specific project defined in the release
    file"""

    branches = []
    for branch in project['branches']:
        repo, ref = next(iter(branch['location'].items()))
        branches.append({
            'project': repo,
            'branch': branch['name'],
            'commit': ref
        })

    for branch in branches:
        create_branch(restapi, branch)


if __name__ == "__main__":
    main()
