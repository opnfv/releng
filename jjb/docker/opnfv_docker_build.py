#!/usr/bin/env python

# Copyright (c) 2017 Ericsson and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0


"""
OPNFV Docker build

It builds the given Dockerfiles in the configuration file and pushes them
to the repository

"""

from io import BytesIO
import logging
import os
import sys
import yaml
import docker

__author__ = "Jose Lausuch <jose.lausuch@ericsson.com>"


LOGGER = logging.getLogger("opnfv docker build")


class FileParser(object):
    """ Parse the Dockerfiles parser """
    def __init__(self, file):
        self.yaml_stream = None
        with open(file, 'r') as data:
            try:
                self.yaml_stream = yaml.load(data)
            except yaml.YAMLError as msg:
                LOGGER.error(msg)

    def get_dockerfiles(self, project):
        try:
            return self.yaml_stream[project]
        except KeyError:
            LOGGER.error("Project '%s' not found in the yaml file", project)


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

    def delete_image(self, image_name):
        """ Removes a given Docker images """
        pass

    def build(self, dockerfile, image_name):
        """
        Builds a Docker image given a dockerfile and complete
        name (name + tag)
        """
        if not os.path.isfile(dockerfile):
            raise IOError('Dockerfile {} does not exist!'.format(dockerfile))

        f = BytesIO(open(dockerfile).read().encode('utf-8'))

        LOGGER.info("Building Docker image %s from %s ...",
                    image_name, dockerfile)
        try:
            self.client.images.build(fileobj=f,
                                     tag=image_name,
                                     nocache=True,
                                     stream=True)
        except Exception as msg:
            LOGGER.error("Problem while building the image %s from %s",
                         image_name, dockerfile)
            raise msg

    def push(self, image_name):
        LOGGER.info("Pushing image %s to Dockerhub...", image_name)


def main():
    """Entry point"""
    project = 'functest'
    tag = 'latest'
    workspace = '/home/ejolaus/repos/functest'
    yaml_file = FileParser('dockerfiles.yaml')
    dockerfiles_list = yaml_file.get_dockerfiles(project)
    handler = OPNFVDockerHandler()
    for key, value in dockerfiles_list.iteritems():
        image_name = ('opnfv/{}:{}'.format(value, tag))
        dockerfile = ('{}/{}'.format(workspace, key))
        handler.build(dockerfile, image_name)
        handler.push(image_name)
    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(message)s')
    sys.exit(main())
