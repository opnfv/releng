#!/bin/bash

set -o errexit
set -o nounset

cd $WORKSPACE/utils/test/testapi/docker/

# Remove previous containers
docker ps -a | grep "opnfv/testapi" | awk '{ print $1 }' | xargs -r docker rm -f

# Remove previous images
docker images | grep "opnfv/testapi" | awk '{ print $3 }' | xargs -r docker rmi -f

# Start build
docker build --no-cache -t opnfv/testapi:$DOCKER_TAG .

# Push Image
docker push opnfv/testapi:$DOCKER_TAG
