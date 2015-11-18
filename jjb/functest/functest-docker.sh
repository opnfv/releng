#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail


echo "Starting the build of Functest Docker."
echo "--------------------------------------------------------"
echo

DOCKER_IMAGE_NAME="opnfv/functest"


# Get tag version
cd $WORKSPACE
git clone https://gerrit.opnfv.org/gerrit/releng

DOCKER_TAG=$($WORKSPACE/releng/utils/calculate_version.sh -t docker \
    -n $DOCKER_IMAGE_NAME)

ret_val=$?
if [ $ret_val -ne 0 ]; then
    echo "Error retrieving the version tag."
    exit 1
else
    echo "Tag version to be build and pushed: $DOCKER_TAG"
fi


# Remove previous running containers if exist
if [[ ! -z $(docker ps -a | grep $DOCKER_IMAGE_NAME) ]]; then
    echo "Removing existing $DOCKER_IMAGE_NAME containers..."
    docker ps | grep $DOCKER_IMAGE_NAME | awk '{{print $1}}' | xargs docker stop
    docker ps -a | grep $DOCKER_IMAGE_NAME | awk '{{print $1}}' | xargs docker rm
fi


# Remove existing images if exist
if [[ ! -z $(docker images | grep $DOCKER_IMAGE_NAME) ]]; then
    echo "Docker images to remove:"
    docker images | head -1 && docker images | grep $DOCKER_IMAGE_NAME
    tags=($(docker images | grep $DOCKER_IMAGE_NAME | awk '{{print $2}}'))
    for tag in "${tags[@]}"; do
        echo "Removing docker image $DOCKER_IMAGE_NAME:$tag..."
        docker rmi $DOCKER_IMAGE_NAME:$tag
    done
fi


# Start the build
echo "Building docker image: $DOCKER_IMAGE_NAME:$DOCKER_TAG..."
cd $WORKSPACE/docker
docker build -t $DOCKER_IMAGE_NAME:$DOCKER_TAG .
echo "Creating tag 'latest'..."
docker tag $DOCKER_IMAGE_NAME:$DOCKER_TAG $DOCKER_IMAGE_NAME:latest

# list the images
echo "Available images are:"
docker images


if [ "$PUSH_IMAGE" == "true" ]; then
    echo "Pushing $DOCKER_IMAGE_NAME:$DOCKER_TAG to the docker registry..."
    echo "--------------------------------------------------------"
    echo
    # Push to the Dockerhub repository
    docker push $DOCKER_IMAGE_NAME:$DOCKER_TAG

    echo "Updating $DOCKER_IMAGE_NAME:latest to the docker registry..."
    docker push $DOCKER_IMAGE_NAME:latest
fi
