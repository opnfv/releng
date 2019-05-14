#!/usr/bin/env python
# SPDX-License-Identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import json
import os
import requests
import subprocess


projects_url="https://gerrit.opnfv.org/gerrit/projects/"
rtd_url="https://opnfv-%s.readthedocs.io/en/stable-%s/objects.inv"
refresh=False

release='hunter'
tag='8.0.0'
participants = [
    "apex",
    "barometer",
    "bottlenecks",
    "clover",
    "container4nfv",
    "cran",
    "doctor",
    "edgecloud",
    "fuel",
    "functest",
    "ipv6",
    "opnfvdocs",
    "ovn4nfv",
    "samplevnf",
    "sfc",
    "vswitchperf",
    "yardstick",
]

# Exclude Gerrit project + inactive/archived
exclude_projects = [
    'All-Projects',
    'All-Users',
    'bamboo',
    'copper',
    'dpacc',
    'escalator',
    'fastpathmetrics',
    'genesis',
    'genesisreq',
    'inspector',
    'joid',
    'lsoapi',
    'movie',
    'multisite',
    'netready',
    'octopus',
    'openretriever',
    'oscar',
    'pinpoint',
    'prediction',
    'promise',
    'rs',
    'securedlab'
]


def extract_project_refs(line, data):
    if 'refs/heads' in line and not line.endswith('^{}'):
        _, head = line.split('\t')
        data['heads'].append(head)
    elif 'refs/tags' in line and not line.endswith('^{}'):
        _, tag = line.split('\t')
        data['tags'].append(tag)

def download_git_metadata():
    response = requests.get(projects_url)
    if not response.status_code == 200:
        print("Error getting project list.")
        exit(1)

    # REPOS="$(curl -L  | tail -n+2 | jq .[].id | tr -d '\"')"
    non_xss_text = response.text[4:]
    full_project_json = json.loads(non_xss_text)
    projects = [project for project in full_project_json]
    projects = list(filter(lambda x: x not in exclude_projects, projects))

    data = []
    for project in projects:
        project_data = {'heads': [], 'tags': []}

        # Get the list of refs + tags
        process = subprocess.Popen(["git", "ls-remote", "--heads", "--tags", "https://gerrit.opnfv.org/gerrit/%s.git" % project],
                stdout=subprocess.PIPE)
        stdout, _ = process.communicate()

        for line in stdout.decode('utf-8').split('\n'):
            extract_project_refs(line, project_data)

        project_data.update({'name': project})
        data.append(project_data)
    return data

def main():
    if refresh or not os.path.exists('git.json'):
       data = download_git_metadata()
       with open('git.json', 'w') as f:
           f.write(json.dumps(data))

    with open('git.json', 'r') as f:
        data = json.load(f)

    # Have list of all projects and their branches/tags
    # Needs list of participating projects

    # Remove non-participating projects

    data[:] = [p for p in data if p.get('name') in participants]
    release_ref = 'refs/heads/stable/%s' % release
    tag_ref = 'refs/tags/opnfv-%s' % tag

    all_projects = [p.get('name') for p in data]
    projects_with_ref = [p for p in data if release_ref in p.get('heads')]
    projects_without_ref = [p for p in data if p not in projects_with_ref]
    projects_with_tag = [p for p in data if tag_ref in p.get('tags')]
    projects_without_tag = [p for p in data if p not in projects_with_tag]

    #print(json.dumps(projects_with_ref))
    #print(json.dumps(projects_without_ref))
    #print(len(projects_with_ref),len(projects_without_ref),len(participants))
    #print([p for p in participants if p not in all_projects])
    #exit(0)

    def stable_branch():
        ## List all participating projects that haven't created a stable
        # branch yet:
        #
        #  7/8 Projects With Stable branches
        #
        #  Projects missing stable branch:
        #   - apex
        print("%d/%d Projects missing stable branch:" % (len(projects_without_ref), len(participants)))
        for project in projects_without_ref:
            print(" - %s" % project.get('name'))

    def documentation():
        ## List all projects missing release documentation:
        #
        #  7/8 Projects with Release Documentation
        #
        #  Projects missing docs:
        #   - apex
        missing_docs = []
        for project in projects_with_ref:
            project_name = project.get('name')
            if project_name == 'opnfvdocs': continue
            documentation_url = rtd_url % (project_name, release)
            response = requests.head(documentation_url)
            if response.status_code != 200:
                missing_docs.append(project)
        len_missing_docs = len(missing_docs)
        if len_missing_docs > 0:
            print("%d/%d Projects with stable branch missing release documentation:" % (len(missing_docs), len(projects_with_ref)))
            for project in missing_docs:
                print(" - %s" % project.get('name'))
        else:
            print("All Projects with stable branches have release documentation")

    def missing_tags():
        ## List all projects missing release tag:
        #
        #  7/8 Projects have tagged their X release
        #
        #  Projects missing release tag:
        #   - apex
        print("%d/%d Projects missing stable tag:" % (len(projects_without_tag), len(participants)))
        for project in projects_without_tag:
            print(" - %s" % project.get('name'))

    def have_tags():
        ## List all projects with stable tags and their version tags
        print("%d/%d Projects with stable tag:" % (len(projects_with_tag), len(participants)))
        for project in projects_with_tag:
            stable_tags = [tag for tag in project.get('tags') if tag.startswith('refs/tags/opnfv-8')]
            print(" - %s (%s)" % (project.get('name'),
                    ", ".join([tag.split('refs/tags/')[1] for tag in
                        stable_tags])))

    stable_branch()
    missing_tags()
    documentation()
    have_tags()


if __name__ == "__main__":
    main()
