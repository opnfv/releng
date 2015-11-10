#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail


echo "Starting the build of Functest Docker."
echo "--------------------------------------------------------"
echo

DOCKER_IMAGE_NAME="opnfv/functest"

# Get tag version
DOCKER_TAG=$(../../utils/calculate_version.sh -t docker -n $DOCKER_IMAGE_NAME)

ret_val=$?
if [ $ret_val -ne 0 ]; then
    echo "Error retrieving the version tag."
    exit 1
else
    echo "Tag version to be build and pushed: $DOCKER_TAG"
fi

# Remove previous running containers
echo "Removing existing $DOCKER_IMAGE_NAME containers..."
docker ps | grep $DOCKER_IMAGE_NAME | awk '{{print $1}}' | xargs docker stop &>/dev/null
docker ps -a | grep $DOCKER_IMAGE_NAME | awk '{{print $1}}' | xargs docker rm &>/dev/null

# Remove existing images
echo "Removing existing $DOCKER_IMAGE_NAME images..."
docker images | grep $DOCKER_IMAGE_NAME | awk '{{print $3}}' | xargs docker rmi &>/dev/null


# Start the build
echo "Starting image build of $DOCKER_IMAGE_NAME:$DOCKER_TAG..."
cd $WORKSPACE/docker/
docker build -t $DOCKER_IMAGE_NAME:$DOCKER_TAG .

# list the images
echo "Available images are:"
docker images


if [ "$PUSH_IMAGE" == "true" ]; then
    echo "Pushing $DOCKER_IMAGE_NAME:$DOCKER_TAG to the docker registry..."
    echo "--------------------------------------------------------"
    echo
    # Push to the Dockerhub repository
    docker push $DOCKER_IMAGE_NAME:$DOCKER_TAG
fi
