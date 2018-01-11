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

from requests.compat import quote, unquote
from requests.exceptions import RequestException

from pygerrit2.rest import GerritRestAPI
from pygerrit2.rest.auth import HTTPBasicAuthFromNetrc


logging.basicConfig(level=logging.INFO)


def create_branch(api, branch):
    """
    Create a branch using the Gerrit REST API
    """
    logger = logging.getLogger()
    # NOTE: quote is used here to escape the '/' in branch name, by
    # default '/' is listed in 'safe' characters which aren't escaped.
    # quote is not used in the data of the PUT request, as it is not
    # required
    arguments = dict(
        project=branch['repo'],
        branch=quote(branch['ref'], ''),
        commit=branch['location']
    )
    # Adding this header will keep Gerrit from overwriting the resource
    # and return a 412 instead of a 409 response.
    headers = {'If-None-Match': '*'}

    branch_data = """
    {
      "ref": "%s"
      "revision": "%s"
    }""" % (branch['ref'], branch['location'])

    # First verify the commit exists, otherwise the branch will be
    # created at HEAD
    try:
        request = api.get("/projects/%(project)s/commits/%(commit)s" %
                          arguments)
        logger.debug(request)
        logger.debug("Commit exists: %(commit)s", arguments)
    except RequestException as err:
        arguments['branch'] = unquote(arguments['branch'])
        if err.response.status_code in [404]:
            logger.warn("Commit %(commit)s for %(project)s:%(branch)s does"
                        " not exist. Not creating branch.", arguments)
        else:
            logger.error(err)
        # Skip trying to create the branch and quit
        quit(1)

    # Try to create the branch and let us know if it already exist.
    try:
        request = api.put("/projects/%(project)s/branches/%(branch)s" %
                          arguments, branch_data, headers=headers)
        logger.info("Branch %(branch)s for %(project)s successfully created",
                    arguments)
    except RequestException as err:
        if err.response.status_code in [412, 409]:
            logger.info("Branch %s already created for %s",
                        unquote(arguments['branch']), arguments['project'])
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
        branches.append({
            'repo': branch['repo'],
            'ref': branch['name'],
            'location': branch['location']
        })

    for branch in branches:
        create_branch(restapi, branch)


if __name__ == "__main__":
    main()
