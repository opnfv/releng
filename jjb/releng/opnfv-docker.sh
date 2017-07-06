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

HOST_ARCH=$(uname -m)

# Look for the special file dockerfile-list.txt.  If this exists, use that
# as the full list of all Dockerfiles to build.  The content should be
# single file names with directory relative to $WORKSPACE and a hyphen for
# the container name.  For exmaple, the content could be:
#   docker/Dockerfile (this would be the same as what exists today)
#   another/dir/Dockerfile-name (this would build project-name)
DOCKERFILE_LIST=$WORKSPACE/docker/dockerfile-list.txt
declare -a DOCKERFILES

if [ -f ${DOCKERFILE_LIST} ] ; then
    IFS="\n" readarray DOCKERFILES < ${DOCKERFILE_LIST}
else
    DOCKERFILES[0]=${DOCKERFILE}
fi

for DOCKERFILE in "${DOCKERFILES[@]}"; do

    DOCKER_IMAGE_NAME=${DOCKERFILE##*-}

    if [ $DOCKER_IMAGE_NAME == $DOCKERFILE ]; then
        # Backwards compatibility - if the dockerfile does not contain
        # a hyphen (ie: Dockerfile vs Dockerfile-submodule) then use it as
        # the actual name of the image.
        DOCKER_IMAGE_NAME=${DOCKER_REPO_NAME}
        DOCKERFILE_DIR=`dirname $DOCKERFILE`
        DOCKERFILE=`basename $DOCKERFILE`
    else
        # The dockerfile name is different, use the repo_name (ie: project
        # name) plus the name of the docker file after the hyphen as the
        # image to build.  For example, directory/Dockerfile-alternate
        # will translate to "opnfv/project-alternate" as the image name to
        # push.
        DOCKER_IMAGE_NAME=`echo ${DOCKER_REPO_NAME}-${DOCKER_IMAGE_NAME}`
        DOCKERFILE_DIR=`dirname $DOCKERFILE`
        DOCKERFILE=`basename $DOCKERFILE`
    fi


    echo "Starting opnfv-docker for $DOCKER_IMAGE_NAME ..."
    echo "  using $DOCKERFILE_DIR/$DOCKERFILE"
    echo "--------------------------------------------------------"
    echo

    cd $WORKSPACE/$DOCKERFILE_DIR

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
    if [[ -n "$(docker ps -a | grep $DOCKER_IMAGE_NAME)" ]]; then
        echo "Removing existing $DOCKER_IMAGE_NAME containers..."
        docker ps -a | grep $DOCKER_IMAGE_NAME | awk '{print $1}' | xargs docker rm -f
        t=60
        # Wait max 60 sec for containers to be removed
        while [[ $t -gt 0 ]] && [[ -n "$(docker ps| grep $DOCKER_IMAGE_NAME)" ]]; do
            sleep 1
            let t=t-1
        done
    fi


    # Remove existing images if exist
    if [[ -n "$(docker images | grep $DOCKER_IMAGE_NAME)" ]]; then
        echo "Docker images to remove:"
        docker images | head -1 && docker images | grep $DOCKER_IMAGE_NAME
        image_ids=($(docker images | grep $DOCKER_IMAGE_NAME | awk '{print $3}'))
        for id in "${image_ids[@]}"; do
            if [[ -n "$(docker images|grep $DOCKER_IMAGE_NAME|grep $id)" ]]; then
                echo "Removing docker image $DOCKER_IMAGE_NAME:$id..."
                docker rmi -f $id
            fi
        done
    fi

    if [ ! -f "${DOCKERFILE}" ]; then
        # If this is expected to be a Dockerfile for other arch than x86
        # and it does not exist, but there is a patch for the said arch,
        # then apply the patch and create the Dockerfile.${HOST_ARCH} file
        if [[ "${DOCKERFILE}" == *"${HOST_ARCH}" && \
              -f "Dockerfile.${HOST_ARCH}.patch" ]]; then
            patch -o Dockerfile."${HOST_ARCH}" Dockerfile \
            Dockerfile."${HOST_ARCH}".patch
        else
            echo "ERROR: No Dockerfile or ${HOST_ARCH} patch found."
            exit 1
        fi
    fi

    # Start the build
    echo "Building docker image: $DOCKER_IMAGE_NAME:$DOCKER_TAG"
    echo "--------------------------------------------------------"
    echo
    cmd="docker build --no-cache -t $DOCKER_IMAGE_NAME:$DOCKER_TAG --build-arg BRANCH=$BUILD_BRANCH
        -f $DOCKERFILE ."

    echo ${cmd}
    ${cmd}


    # list the images
    echo "Available images are:"
    docker images

    # Push image to Dockerhub
    if [[ "$PUSH_IMAGE" == "true" ]]; then
        echo "Pushing $DOCKER_IMAGE_NAME:$DOCKER_TAG to the docker registry..."
        echo "--------------------------------------------------------"
        echo
        docker push $DOCKER_IMAGE_NAME:$DOCKER_TAG
    fi

done