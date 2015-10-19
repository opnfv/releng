#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Starting the build of Functest Docker."
echo "--------------------------------------------------------"
echo

# Remove previous running containers
$ docker ps | grep opnfv/functest | awk '{print $1}' | xargs docker stop &>/dev/null
$ docker ps -a | grep opnfv/functest | awk '{print $1}' | xargs docker rm &>/dev/null


# Remove existing images
$ docker images | grep opnfv/functest | awk '{print $3}' | xargs docker rmi &>/dev/null

# start the build
cd $WORKSPACE/docker/
docker build -t opnfv/functest .

# list the images
docker images
