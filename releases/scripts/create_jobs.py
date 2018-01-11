"""
Create Gerrit Branchs
"""

import argparse
import ConfigParser
import logging
import os
from jenkins_jobs import local_yaml
import yaml

logging.basicConfig(level=logging.INFO)


def replace_string(original, new, d):
    """
    Recursively iterate through a dictionary replacing any occurance of
    'original' string with 'new'.
    """
    for k, v in d.iteritems():
        if isinstance(v, dict):
            replace_string(original, new, v)
        if isinstance(v, str):
            d[k] = v.replace(original, new)
            



def main():
    """
    Create Jenkins Jobs for stable branches in Release File
    """
    logger = logging.getLogger('jobs')

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', type=argparse.FileType('r'), required=True)
    args = parser.parse_args()

    project = yaml.load(args.file)

    arg = {'project': project['branches'][0]['repo'],
           'branch': project['branches'][0]['name']}

    logger.info("> Creating Jenkins Jobs for %(project)s" % arg)
    if project['branches'][0]['repo'] == 'ci-management':
        return

    job_file = "jjb/%(project)s/%(project)s.yml" % arg
    yaml_jjb = local_yaml.load(open(job_file))

    for stream in yaml_jjb[0]['project']['stream']:
        if 'master' in stream:
            new_stable = stream.copy()
            replace_string('master', 'euphrates', new_stable)
            print(new_stable)



if __name__ == "__main__":
    main()
