"""
Create Gerrit Branchs
"""

import ConfigParser
import logging
import os
import yaml

from requests.compat import quote, unquote
from requests.exceptions import RequestException

from pygerrit2.rest import GerritRestAPI
from pygerrit2.rest.auth import HTTPBasicAuthFromNetrc


def create_branch(api, branch):
    """
    Create a branch using the Gerrit REST API
    """
    # Note: quote is used here to escape the '/' in branch name, by
    # default '/' is listed in 'safe' characters which aren't escaped
    arguments = dict(
        project=branch['repo'],
        branch=quote(branch['ref'], '')
    )
    # Adding this header will keep Gerrit from overwriting the resource
    # and return a 412 instead of a 409 response.
    headers = {'If-None-Match': '*'}

    data = """
    {
      "ref": "%s"
      "revision": "%s"
    }""" % (branch['ref'], branch['location'])


    try:
        request = api.put("/projects/%(project)s/branches/%(branch)s" % arguments,
                           data, headers=headers)
        resp_json = request[0]
        response = request[1]
        logging.info("Created %s branch for %s",
                     branch['ref'], arguments['project'])
        logging.debug("Success %s: Created %s from %s", response.status_code,
                     resp_json['ref'], resp_json['revision'])
    except RequestException as err:
        if err.response.status_code in [412, 409]:
            logging.info("Branch %s already created for %s",
                         unquote(arguments['branch']), arguments['project'])
        else:
            logging.error("Error: %s", str(err))


def main():
    """Given a yamlfile that follows the release syntax, create branches
    in Gerrit listed under branches"""

    config = ConfigParser.ConfigParser()
    config.read('defaults.cfg')
    config.read([os.path.expanduser('~/releases.cfg'), 'releases.cfg'])

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        level=logging.INFO)

    gerrit_url = config.get('gerrit', 'url')
    try:
        auth = HTTPBasicAuthFromNetrc(url=gerrit_url)
    except ValueError, e:
        logging.error("%s for %s", e, gerrit_url)
        quit(1)
    restapi = GerritRestAPI(url=gerrit_url, auth=auth)

    # TODO: Pass the file location as an argument
    release = yaml.load(open('../euphrates/apex.yaml'))

    branches = []
    for branch in release['branches']:
        branches.append({
            'repo': branch['repo'],
            'ref': branch['name'],
            'location': branch['location']
        })

    for branch in branches:
        create_branch(restapi, branch)


if __name__ == "__main__":
    main()
