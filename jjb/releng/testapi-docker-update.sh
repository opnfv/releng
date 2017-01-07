#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

cd $WORKSPACE/utils/test/testapi/docker/

# Remove previous images
if [[ -n "$(docker images | grep opnfv/testapi)" ]]; then
    docker images | grep opnfv/testapi | awk '{ print $3; }' | xargs -r docker rmi -f
fi

# Start build
docker build --no-cache -t opnfv/testapi:$DOCKER_TAG .

# Push Image
docker push opnfv/testapi:$DOCKER_TAG
