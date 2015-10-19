#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail


echo "Starting the build of Functest Docker."
echo "--------------------------------------------------------"
echo

NAME="opnfv/functest"

# Get tag version
TAG=$(calculate_version.sh -t docker -n ${NAME})
ret_val=$?
if [ $ret_val -nq 0 ]; then
    echo "Error retrieving the version tag."
    exit 1
else
    echo "Tag version to be build and pushed: ${TAG}"
fi

# Remove previous running containers
echo "Removing existing ${NAME} containers..."
docker ps | grep ${NAME} | awk '{print $1}' | xargs docker stop &>/dev/null
docker ps -a | grep ${NAME} | awk '{print $1}' | xargs docker rm &>/dev/null

# Remove existing images
echo "Removing existing ${NAME} images..."
docker images | grep ${NAME} | awk '{print $3}' | xargs docker rmi &>/dev/null


# Start the build
echo "Starting image build of ${NAME}:${TAG}..."
cd $WORKSPACE/docker/
docker build -t ${NAME}:${TAG} .

# list the images
echo "Available images are:"
docker images


if [ ${PUSH_IMAGE} == true ]; then
    echo "Pushing ${NAME}:${TAG} to the docker registry..."
    echo "--------------------------------------------------------"
    echo
    # Push to the Dockerhub repository
    docker push ${NAME}:${TAG}
fi
