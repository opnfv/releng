#!/bin/bash

set -o errexit
set -o nounset

cd $WORKSPACE/utils/test/$MODULE_NAME/docker/

# Remove previous containers
docker ps -a | grep "opnfv/$MODULE_NAME" | awk '{ print $1 }' | xargs -r docker rm -f

# Remove previous images
docker images | grep "opnfv/$MODULE_NAME" | awk '{ print $3 }' | xargs -r docker rmi -f

# Start build
docker build --no-cache -t opnfv/$MODULE_NAME:$DOCKER_TAG .

# Push Image
docker push opnfv/$MODULE_NAME:$DOCKER_TAG
