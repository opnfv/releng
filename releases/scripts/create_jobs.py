"""
Create Gerrit Branchs
"""

import argparse
import copy
import logging
import yaml

from jenkins_jobs import local_yaml


logging.basicConfig(level=logging.INFO)


def replace_string(original, new, dictionary):
    """
    Recursively iterate through a dictionary replacing any occurance of
    'original' string, in keys or values, with 'new'.
    """
    for key, value in dictionary.iteritems():
        if isinstance(value, dict):
            replace_string(original, new, value)
        if key == original:
            dictionary[new] = value
            del dictionary[original]
        if isinstance(value, str):
            dictionary[key] = value.replace(original, new)


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
    project_config = yaml_jjb[0]['project']

    for stream in project_config['stream']:
        if 'master' in stream:
            new_stable = copy.deepcopy(stream)
            replace_string('master', 'fraser', new_stable)
            project_config['stream'].append(new_stable)
    # TODO: Need to pull out parts of jenkins_jobs LocalDumper, or look
    # into using ruamel.yaml to edit the files in place, as this
    # modifies almost every line of the file.
    local_yaml.dump(yaml_jjb, open(job_file, 'w'))



if __name__ == "__main__":
    main()
