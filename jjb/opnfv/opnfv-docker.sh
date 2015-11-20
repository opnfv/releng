#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail


echo "Starting the build of Docker image."
echo "--------------------------------------------------------"
echo


# Get tag version
cd $WORKSPACE
git clone https://gerrit.opnfv.org/gerrit/releng

DOCKER_TAG=$($WORKSPACE/releng/utils/calculate_version.sh -t docker \
    -n $DOCKER_REPO_NAME)

ret_val=$?
if [ $ret_val -ne 0 ]; then
    echo "Error retrieving the version tag."
    exit 1
else
    echo "Tag version to be build and pushed: $DOCKER_TAG"
fi


# Remove previous running containers if exist
if [[ ! -z $(docker ps -a | grep $DOCKER_REPO_NAME) ]]; then
    echo "Removing existing $DOCKER_REPO_NAME containers..."
    docker ps | grep $DOCKER_REPO_NAME | awk '{{print $1}}' | xargs docker stop
    docker ps -a | grep $DOCKER_REPO_NAME | awk '{{print $1}}' | xargs docker rm
fi


# Remove existing images if exist
if [[ ! -z $(docker images | grep $DOCKER_REPO_NAME) ]]; then
    echo "Docker images to remove:"
    docker images | head -1 && docker images | grep $DOCKER_REPO_NAME
    image_tags=($(docker images | grep $DOCKER_REPO_NAME | awk '{{print $2}}'))
    for tag in "${{image_tags[@]}}"; do
        echo "Removing docker image $DOCKER_REPO_NAME:$tag..."
        docker rmi $DOCKER_REPO_NAME:$tag
    done
fi


# Start the build
echo "Building docker image: $DOCKER_REPO_NAME:$DOCKER_TAG..."
# cd to directory where Dockerfile is located
if [[ "$DOCKER_REPO_NAME" == "opnfv/functest" ]]; then
    cd $WORKSPACE/docker
elif [[ "$DOCKER_REPO_NAME" == "opnfv/functest" ]]; then
    cd $WORKSPACE/ci/docker/yardstick-ci
else
    echo "DOCKER_REPO_NAME parameter not valid: $DOCKER_REPO_NAME"
    exit 1
fi

docker build -t $DOCKER_REPO_NAME:$DOCKER_TAG .
echo "Creating tag 'latest'..."
docker tag $DOCKER_REPO_NAME:$DOCKER_TAG $DOCKER_REPO_NAME:latest

# list the images
echo "Available images are:"
docker images

# Push image to Dockerhub
if [ "$PUSH_IMAGE" == "true" ]; then
    echo "Pushing $DOCKER_REPO_NAME:$DOCKER_TAG to the docker registry..."
    echo "--------------------------------------------------------"
    echo
    # Push to the Dockerhub repository
    docker push $DOCKER_REPO_NAME:$DOCKER_TAG

    echo "Updating $DOCKER_REPO_NAME:latest to the docker registry..."
    docker push $DOCKER_REPO_NAME:latest
fi
