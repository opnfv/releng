#!/usr/bin/env python

# Copyright (c) 2017 Ericsson and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0


'''
OPNFV Docker build

It builds the given Dockerfiles in the configuration file and pushes them
to the repository

'''

import logging
import os
import sys
import yaml
import docker

__author__ = 'Jose Lausuch <jose.lausuch@ericsson.com>'


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s')
LOGGER = logging.getLogger('opnfv_docker_build')
if os.getenv('DEBUG').lower() == "true":
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)


def get_env():
    params = {}
    try:
        params.update({'project': os.environ['PROJECT']})
        params.update({'branch': os.environ['BRANCH']})
        params.update({'workspace': os.environ['WORKSPACE']})
        params.update({'tag': get_tag_from_branch(os.environ['BRANCH'])})
    except KeyError as msg:
        LOGGER.error("Missing environment variable\n")
        raise msg
    return params


def get_dockerfiles(file, project):
        yaml_stream = None
        with open(file, 'r') as data:
            try:
                yaml_stream = yaml.safe_load(data)
            except yaml.YAMLError as msg:
                LOGGER.error(msg)
        try:
            return yaml_stream[project]
        except KeyError:
            LOGGER.error("Project '%s' not found in the yaml file", project)


def get_tag_from_branch(branch_name):
    if branch_name == "master":
        return "latest"
    elif "stable" in branch_name:
        return "stable"


class OPNFVDockerHandler(object):
    """ Docker images build process """
    def __init__(self):
        self.client = docker.from_env()

    def get_images(self):
        """ Returns all Docker images in the system """
        try:
            return docker.images.list()
        except Exception as msg:
            LOGGER.error("Problem while fetching the Docker images from "
                         "the system")
            raise msg

    def delete_image(self, image_name, tag):
        """ Removes a given Docker images """
        LOGGER.info("Removing Docker image %s:%s ...", image_name, tag)
        image = ('{}:{}'.format(image_name, tag))
        try:
            self.client.images.remove(image=image, force=True, noprune=False)
        except Exception as msg:
            LOGGER.error("Problem while removing the image %s:%s",
                         image_name, tag)
            raise msg

    def build(self, dockerfile, repository, tag):
        """
        Builds a Docker image given a Dockerfile and complete
        name (name + tag)
        """
        if not os.path.isfile(dockerfile):
            raise IOError('Dockerfile {} does not exist!'.format(dockerfile))

        image = ('{}:{}'.format(repository, tag))
        LOGGER.info("\n\n"
                    "+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                    "Docker build:\n"
                    "  image: %s\n"
                    "  dockerfile: %s\n"
                    "+++++++++++++++++++++++++++++++++++++++++++++++++++++++",
                    image, dockerfile)
        try:
            path = os.path.split(dockerfile)[0]
            image = self.client.images.build(path=path,
                                             dockerfile=dockerfile,
                                             tag=image,
                                             nocache=True,
                                             rm=True,
                                             forcerm=True)
            LOGGER.debug(image)
        except Exception as msg:
            LOGGER.error("Problem while building the image %s from %s",
                         image, dockerfile)
            raise msg

        LOGGER.info("Image built successfully")

    def push(self, repository, tag):
        LOGGER.info("\n\n"
                    "+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                    "Docker push:\n"
                    "  image: %s:%s\n"
                    "+++++++++++++++++++++++++++++++++++++++++++++++++++++++",
                    repository, tag)
        try:
            output = self.client.images.push(repository=repository, tag=tag)
            LOGGER.debug(output)
        except Exception as msg:
            LOGGER.error("Problem while pushing the image %s:%s to dockerhub",
                         repository, tag)
            raise msg
        LOGGER.info("Image pushed successfully")


def main():
    """Entry point"""
    params = get_env()
    LOGGER.info("Environment: %s", params)
    handler = OPNFVDockerHandler()
    yaml_file = (os.path.dirname(os.path.abspath(__file__)) +
                 '/dockerfiles.yaml')
    dockerfiles_list = get_dockerfiles(yaml_file, params['project'])
    LOGGER.info("Images to be built: %s", dockerfiles_list)
    for key, value in dockerfiles_list.iteritems():
        repository = ('opnfv/{}'.format(value))
        dockerfile = ('{}/{}'.format(params['workspace'], key))
        handler.build(dockerfile, repository, params['tag'])
        handler.push(repository, params['tag'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
