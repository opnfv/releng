#!/bin/bash

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

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
