#!/bin/bash
##############################################################################
# Copyright (c) 2016 ZTE and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
# Remove previous running containers if exist
if [[ ! -z $(docker ps -a | grep opnfv/qtip) ]]; then
    echo "Removing existing opnfv/qtip containers..."
    # workaround: sometimes it throws an error when stopping qtip container.
    # To make sure ci job unblocked, remove qtip container by force without stopping it.
    docker ps -a | grep opnfv/qtip | awk '{print $1}' | xargs docker rm -f >"/dev/null"
fi

# Remove existing images if exist
if [[ ! -z $(docker images | grep opnfv/qtip) ]]; then
    echo "Docker images to remove:"
    docker images | head -1 && docker images | grep opnfv/qtip
    image_tags=($(docker images | grep opnfv/qtip | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        echo "Removing docker image opnfv/qtip:$tag..."
        docker rmi opnfv/qtip:$tag
    done
fi
