#!/bin/bash

set -o errexit
set -o nounset

cd $WORKSPACE/utils/test/$1/docker/

# Remove previous containers
docker ps -a | grep "opnfv/$1" | awk '{ print $1 }' | xargs -r docker rm -f

# Remove previous images
docker images | grep "opnfv/$1" | awk '{ print $3 }' | xargs -r docker rmi -f

# Start build
docker build --no-cache -t opnfv/$1:$DOCKER_TAG .

# Push Image
docker push opnfv/$1:$DOCKER_TAG
