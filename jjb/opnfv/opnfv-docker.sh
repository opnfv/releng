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
    # Abort this job since it will colide and might mess up the current one.
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

# If we just want to update the latest_stable image
if [[ "$UPDATE_LATEST_STABLE" == "true" ]]; then
    echo "Pulling $DOCKER_REPO_NAME:$STABLE_TAG ..."
    docker pull $DOCKER_REPO_NAME:$STABLE_TAG
    if [[ $? -ne 0 ]]; then
        echo "ERROR: The image $DOCKER_REPO_NAME with tag $STABLE_TAG does not exist."
        exit 1
    fi
    docker tag -f $DOCKER_REPO_NAME:$STABLE_TAG $DOCKER_REPO_NAME:latest_stable
    echo "Pushing $DOCKER_REPO_NAME:latest_stable ..."
    docker push $DOCKER_REPO_NAME:latest_stable
    exit 0
fi


# cd to directory where Dockerfile is located
if [[ "$DOCKER_REPO_NAME" == "opnfv/bottlenecks" ]]; then
    cd $WORKSPACE/ci/docker
elif [[ "$DOCKER_REPO_NAME" == "opnfv/cperf" ]]; then
    cd $WORKSPACE/docker
elif [[ "$DOCKER_REPO_NAME" == "opnfv/functest" ]]; then
    cd $WORKSPACE/docker
elif [[ "$DOCKER_REPO_NAME" == "opnfv/qtip" ]]; then
    cd $WORKSPACE/docker
elif [[ "$DOCKER_REPO_NAME" == "opnfv/storperf" ]]; then
    cd $WORKSPACE/docker
elif [[ "$DOCKER_REPO_NAME" == "opnfv/yardstick" ]]; then
    cd $WORKSPACE/tests/ci/docker/yardstick-ci
else
    echo "ERROR: DOCKER_REPO_NAME parameter not valid: $DOCKER_REPO_NAME"
    exit 1
fi

# Get tag version
branch="${GIT_BRANCH##origin/}"
echo "Current branch: $branch"

if [[ "$branch" == "master" ]]; then
    DOCKER_TAG="master"
    DOCKER_BRANCH_TAG="latest"
else
    git clone https://gerrit.opnfv.org/gerrit/releng $WORKSPACE/releng

    DOCKER_TAG=$($WORKSPACE/releng/utils/calculate_version.sh -t docker \
        -n $DOCKER_REPO_NAME)
    DOCKER_BRANCH_TAG="stable"

    ret_val=$?
    if [[ $ret_val -ne 0 ]]; then
        echo "Error retrieving the version tag."
        exit 1
    fi
fi
echo "Tag version to be build and pushed: $DOCKER_TAG"


# Start the build
echo "Building docker image: $DOCKER_REPO_NAME:$DOCKER_BRANCH_TAG"

if [[ $DOCKER_REPO_NAME == *"functest"* ]]; then
    docker build --no-cache -t $DOCKER_REPO_NAME:$DOCKER_BRANCH_TAG --build-arg BRANCH=$branch .
else
    docker build --no-cache -t $DOCKER_REPO_NAME:$DOCKER_BRANCH_TAG .
fi

echo "Creating tag '$DOCKER_TAG'..."
docker tag -f $DOCKER_REPO_NAME:$DOCKER_BRANCH_TAG $DOCKER_REPO_NAME:$DOCKER_TAG

# list the images
echo "Available images are:"
docker images

# Push image to Dockerhub
if [[ "$PUSH_IMAGE" == "true" ]]; then
    echo "Pushing $DOCKER_REPO_NAME:$DOCKER_TAG to the docker registry..."
    echo "--------------------------------------------------------"
    echo
    # Push to the Dockerhub repository
    echo "Pushing $DOCKER_REPO_NAME:$DOCKER_BRANCH_TAG ..."
    docker push $DOCKER_REPO_NAME:$DOCKER_BRANCH_TAG

    echo "Pushing $DOCKER_REPO_NAME:$DOCKER_TAG ..."
    docker push $DOCKER_REPO_NAME:$DOCKER_TAG
fi
