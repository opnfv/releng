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

count=30 # docker build jobs might take up to ~30 min
while [[ -n `ps -ef|grep 'docker build'|grep -v grep` ]]; do
    echo "Build in progress. Waiting..."
    sleep 60
    count=$(( $count - 1 ))
    if [ $count -eq 0 ]; then
        echo "Timeout. Aborting..."
        exit 1
    fi
done

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

cd "$WORKSPACE/$DOCKER_DIR" || exit 1
HOST_ARCH="$(uname -m)"
#If there is a patch for other arch then x86, apply the patch and
#replace Dockerfile file
dockerfile_patch=$(find . -iname "Dockerfile.${HOST_ARCH}.patch")
if [[ -n ${dockerfile_patch} ]]; then
    for patch in ${dockerfile_patch}; do
        patch -f -p1 < "$patch"
    done
fi

# Get tag version
echo "Current branch: $BRANCH"

BUILD_BRANCH=$BRANCH

if [[ "$BRANCH" == "master" ]]; then
    DOCKER_TAG="latest"
elif [[ -n "${RELEASE_VERSION-}" ]]; then
    DOCKER_TAG=${BRANCH##*/}.${RELEASE_VERSION}
    # e.g. danube.1.0, danube.2.0, danube.3.0
else
    DOCKER_TAG="stable"
fi

if [[ -n "${COMMIT_ID-}" && -n "${RELEASE_VERSION-}" ]]; then
    DOCKER_TAG=$RELEASE_VERSION
    BUILD_BRANCH=$COMMIT_ID
fi

# Start the build
echo "Building docker image: $DOCKER_REPO_NAME:$DOCKER_TAG"
echo "--------------------------------------------------------"
echo
cmd="docker build --no-cache -t $DOCKER_REPO_NAME:$DOCKER_TAG --build-arg BRANCH=$BUILD_BRANCH
    -f $DOCKERFILE ."

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
