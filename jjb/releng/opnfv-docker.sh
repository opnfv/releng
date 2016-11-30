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
    image_tags=($(docker images | grep $DOCKER_REPO_NAME | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        if [[ -n "$(docker images|grep $DOCKER_REPO_NAME|grep $tag)" ]]; then
            echo "Removing docker image $DOCKER_REPO_NAME:$tag..."
            docker rmi -f $DOCKER_REPO_NAME:$tag
        fi
    done
fi


# cd to directory where Dockerfile is located
cd $WORKSPACE/docker
if [ ! -f ./Dockerfile ]; then
    echo "ERROR: Dockerfile not found."
    exit 1
fi

# Get tag version
branch="${GIT_BRANCH##origin/}"
echo "Current branch: $branch"

if [[ "$branch" == "master" ]]; then
    DOCKER_TAG="latest"
else
    DOCKER_TAG="stable"
fi

# Start the build
echo "Building docker image: $DOCKER_REPO_NAME:$DOCKER_TAG"
echo "--------------------------------------------------------"
echo
cmd="docker build --no-cache -t $DOCKER_REPO_NAME:$DOCKER_TAG --build-arg BRANCH=$branch ."

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
