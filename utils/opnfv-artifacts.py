#!/usr/bin/python
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 The Linux Foundation and others
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

"""
Generate JSON listing of OPNFV Artifacts

This produces a slimmed down version of metadata provided by Google
Storage for each artifact. Also excludes a large number of uninteresting
files.
"""

from apiclient import discovery
from apiclient.errors import HttpError

import argparse
import json
import os
import sys

api = {
  'projects': {},
  'docs': {},
  'releases': {},
}

releases = [
  'arno.2015.1.0',
  'arno.2015.2.0',
  'brahmaputra.1.0',
]

# List of file extensions to filter out
ignore_extensions = [
  '.buildinfo',
  '.woff',
  '.ttf',
  '.svg',
  '.eot',
  '.pickle',
  '.doctree',
  '.js',
  '.png',
  '.css',
  '.gif',
  '.jpeg',
  '.jpg',
  '.bmp',
]


parser = argparse.ArgumentParser(
             description='OPNFV Artifacts JSON Generator')

parser.add_argument(
        '-k',
        dest='key',
        default='',
        help='API Key for Google Cloud Storage')

parser.add_argument(
        '-p',
        default=None,
        dest='pretty',
        action='store_const',
        const=2,
        help='pretty print the output')

# Parse and assign arguments
args = parser.parse_args()
key = args.key
pretty_print = args.pretty


def output(item, indent=2):
    print(json.dumps(item, sort_keys=True, indent=indent))


def has_gerrit_review(dir_list):
    """
    If a directory contains an integer, it is assumed to be a gerrit
    review number
    """
    for d in dir_list:
        if d.isdigit():
            return int(d)
    return False


def has_release(dir_list):
    """
    Checks if any directory contains a release name
    """
    for d in dir_list:
        if d in releases:
            return d
    return False


def has_documentation(dir_list):
    """
    Checks for a directory specifically named 'docs'
    """
    for d in dir_list:
        if d == 'docs':
            return True
    return False


# Rename this or modify how gerrit review are handled
def has_logs(gerrit_review):
    """
    If a gerrit review exists, create a link to the review
    """
    if gerrit_review:
        return "https://gerrit.opnfv.org/gerrit/#/c/%s" % gerrit_review
    return False



def has_ignorable_extension(filename):
    for extension in ignore_extensions:
        if filename.lower().endswith(extension):
            return True
    return False


def get_results(key):
    """
    Pull down all metadata from artifacts.opnfv.org
    and store it in projects as:
    { 'PROJECT': [file ...], }
    """
    storage = discovery.build('storage', 'v1', developerKey=key)
    files = storage.objects().list(bucket='artifacts.opnfv.org',
                                   fields='nextPageToken,'
                                          'items('
                                              'name,'
                                              'mediaLink,'
                                              'updated,'
                                              'contentType,'
                                              'size'
                                          ')')
    while (files is not None):
        sites = files.execute()

        for site in sites['items']:
            # Filter out unneeded files (js, images, css, buildinfo, etc)
            if has_ignorable_extension(site['name']):
                continue

            # Split /foo/bar/ into ['foo', 'bar'] and remove any extra
            # slashes (ex. /foo//bar/)
            site_split = filter(None, site['name'].split('/'))

            # Don't do anything if we aren't given files multiple
            # directories deep
            if len(site_split) < 2:
                continue

            project = site_split[0]
            name = '/'.join(site_split[1:])
            proxy = "http://build.opnfv.org/artifacts.opnfv.org/%s" % site['name']
            if name.endswith('.html'):
                href = "http://artifacts.opnfv.org/%s" % site['name']
                href_type = 'view'
            else:
                href = site['mediaLink']
                href_type = 'download'

            gerrit = has_gerrit_review(site_split)
            logs = False  # has_logs(gerrit)
            documentation = has_documentation(site_split)
            release = has_release(site_split)

            category = 'project'
            if gerrit:
                category = 'gerrit'
            elif release:
                category = 'release'
            elif logs:
                category = 'logs'

            metadata = {
                'category': category,
                'gerritreview': gerrit,
                'release': release,
                'name': name,
                'size': site['size'],
                'time': site['updated'],
                'contentType': site['contentType'],
                'href': href,
                'href_type': href_type,
                'proxy_href': proxy,
            }

            if project in releases:
                if project not in api['releases']:
                    api['releases'][project] = [metadata]
                else:
                    api['releases'][project].append(metadata)
            else:
                if project not in api['projects']:
                    api['projects'][project] = [metadata]
                else:
                    api['projects'][project].append(metadata)

        files = storage.objects().list_next(files, sites)

    return api


# Fail if there is an invalid response from GCE
try:
    js = get_results(key)
except HttpError as e:
    print >> sys.stderr, e
    exit(1)

output(js, indent=pretty_print)
