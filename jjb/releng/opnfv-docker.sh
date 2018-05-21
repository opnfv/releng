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


echo "Using Docker $(docker --version) on $NODE_NAME"
echo "Starting Docker build for $DOCKER_REPO_NAME ..."
echo "--------------------------------------------------------"
echo

function remove_containers_images()
{
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
}


count=30 # docker build jobs might take up to ~30 min
while [[ -n `ps -ef| grep 'docker build' | grep $DOCKER_REPO_NAME | grep -v grep` ]]; do
    echo "Build or cleanup of $DOCKER_REPO_NAME in progress. Waiting..."
    sleep 60
    count=$(( $count - 1 ))
    if [ $count -eq 0 ]; then
        echo "Timeout. Aborting..."
        exit 1
    fi
done

# Remove the existing containers and images before building
remove_containers_images

DOCKER_PATH=$WORKSPACE/$DOCKER_DIR

cd $DOCKER_PATH || exit 1
HOST_ARCH="$(uname -m)"
#If there is a patch for other arch then x86, apply the patch and
#replace Dockerfile file
dockerfile_patch="Dockerfile.${HOST_ARCH}.patch"
if [[ -f "${dockerfile_patch}" ]]; then
        patch -f Dockerfile -p1 < "${dockerfile_patch}"
fi

# Get tag version
echo "Current branch: $BRANCH"

BUILD_BRANCH=$BRANCH

GERRIT_REFNAME=${GERRIT_REFNAME:-''}
RELEASE_VERSION=${GERRIT_REFNAME/refs\/tags\/}

# If we're being triggered by a comment-added job, then extract the tag
# from the comment and use that as the release version.
# Expected comment format: retag opnfv-x.y.z
if [[ "${GERRIT_EVENT_TYPE:-}" == "comment-added" ]]; then
    RELEASE_VERSION=$(echo "$GERRIT_EVENT_COMMENT_TEXT" | grep 'retag' | awk '{print $2}')
fi

if [[ "$BRANCH" == "master" ]]; then
    DOCKER_TAG="latest"
elif [[ -n "${RELEASE_VERSION-}" ]]; then
    DOCKER_TAG=${RELEASE_VERSION}
    if git checkout ${RELEASE_VERSION}; then
        echo "Successfully checked out the git tag ${RELEASE_VERSION}"
    else
        echo "The tag ${RELEASE_VERSION} doesn't exist in the repository. Existing tags are:"
        git tag
        exit 1
    fi
else
    DOCKER_TAG="stable"
fi

if [[ -n "${COMMIT_ID-}" && -n "${RELEASE_VERSION-}" ]]; then
    DOCKER_TAG=$RELEASE_VERSION
    BUILD_BRANCH=$COMMIT_ID
fi

ARCH_BUILD_ARG=""
ARCH_TAG=${ARCH_TAG:-}
if [[ -n "${ARCH_TAG}" ]]; then
    DOCKER_TAG=${ARCH_TAG}-${DOCKER_TAG}
    ARCH_BUILD_ARG="--build-arg ARCH=${ARCH_TAG}"
fi

# Start the build
echo "Building docker image: $DOCKER_REPO_NAME:$DOCKER_TAG"
echo "--------------------------------------------------------"
echo
cmd="docker build --pull=true --no-cache -t $DOCKER_REPO_NAME:$DOCKER_TAG --build-arg BRANCH=$BUILD_BRANCH
    $ARCH_BUILD_ARG
    -f $DOCKERFILE $DOCKER_PATH"

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

# Remove the existing containers and images after building
remove_containers_images
