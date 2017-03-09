#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail



echo "Starting opnfv-docker for $DOCKER_REPO_NAME ..."
echo "--------------------------------------------------------"
echo


if [[ -n $(ps -ef|grep 'docker build'|grep -v grep) ]]; then
    echo "There is already another build process in progress:"
    echo $(ps -ef|grep 'docker build'|grep -v grep)
    # Abort this job since it will collide and might mess up the current one.
    echo "Aborting..."
    exit 1
fi

# Remove previous running containers if exist
if [[ -n "$(docker ps -a | grep $DOCKER_REPO_NAME)" ]]; then
    echo "Removing existing $DOCKER_REPO_NAME containers..."
    docker ps -a | grep $DOCKER_REPO_NAME | awk '{print $1}' | xargs docker rm -f
    t=60
    # Wait max 60 sec for containers to be removed
    while [[ $t -gt 0 ]] && [[ -n "$(docker ps| grep $DOCKER_REPO_NAME)" ]]; do
        sleep 1
        let t=t-1
    done
fi


# Remove existing images if exist
if [[ -n "$(docker images | grep $DOCKER_REPO_NAME)" ]]; then
    echo "Docker images to remove:"
    docker images | head -1 && docker images | grep $DOCKER_REPO_NAME
    image_ids=($(docker images | grep $DOCKER_REPO_NAME | awk '{print $3}'))
    for id in "${image_ids[@]}"; do
        if [[ -n "$(docker images|grep $DOCKER_REPO_NAME|grep $id)" ]]; then
            echo "Removing docker image $DOCKER_REPO_NAME:$id..."
            docker rmi -f $id
        fi
    done
fi

cd $WORKSPACE/docker
if [ ! -f ${DOCKERFILE} ]; then
    # If this is supposed to be an aarch64 Dockerfile and it does not exist
    # but an aarch64 patch exists, then apply the patch and create the
    # Dockerfile.aarch file
    if [ ${DOCKERFILE} contains "aarch64" ] && \
       [ -f 0001-Apply-aarch64-to-Dockerfile.patch]; then
        cmd="git am ${PWD}/0001-Adapt-Dockerfile-to-aarch64.patch"
        ${cmd}
        mv Dockerfile Dockerfile.aarch64
    else
        echo "ERROR: Dockerfile not found."
        exit 1
    fi
fi

# Get tag version
echo "Current branch: $BRANCH"

if [[ "$BRANCH" == "master" ]]; then
    DOCKER_TAG="latest"
else
    if [[ "$RELEASE_VERSION" != "" ]]; then
        release=${BRANCH##*/}
        DOCKER_TAG=${release}.${RELEASE_VERSION}
        # e.g. colorado.1.0, colorado.2.0, colorado.3.0
    else
        DOCKER_TAG="stable"
    fi
fi

# Start the build
echo "Building docker image: $DOCKER_REPO_NAME:$DOCKER_TAG"
echo "--------------------------------------------------------"
echo
if [[ $DOCKER_REPO_NAME == *"dovetail"* ]]; then
    cmd="docker build --no-cache -t $DOCKER_REPO_NAME:$DOCKER_TAG -f $DOCKERFILE ."
else
    cmd="docker build --no-cache -t $DOCKER_REPO_NAME:$DOCKER_TAG --build-arg BRANCH=$BRANCH
        -f $DOCKERFILE ."
fi

echo ${cmd}
${cmd}


# list the images
echo "Available images are:"
docker images

# Push image to Dockerhub
if [[ "$PUSH_IMAGE" == "true" ]]; then
    echo "Pushing $DOCKER_REPO_NAME:$DOCKER_TAG to the docker registry..."
    echo "--------------------------------------------------------"
    echo
    docker push $DOCKER_REPO_NAME:$DOCKER_TAG
fi
