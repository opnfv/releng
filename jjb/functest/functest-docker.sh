#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail


function calculate_tag() {
    url="https://registry.hub.docker.com/v2/repositories/opnfv/functest/tags/"
    tag_json=$(curl $url | python -mjson.tool | grep brahmaputra | head -1)
    tag=$(echo $tag_json | sed 's/^.*bra/bra/' | sed 's/\"\,//')
    #ex: tag=brahmaputra.2016.0.2
    tag_arr=(${tag//./ })
    tag_release_name=${tag_arr[0]}
    tag_year=${tag_arr[1]}
    tag_release=${tag_arr[2]}
    tag_version=${tag_arr[3]}
    tag_version_new=$(($tag_version+1))
    tag_new=${tag_release_name}.${tag_year}.${tag_release}.${tag_version_new}
    echo $tag_new
}

# log info to console
echo "Starting the build of Functest Docker."
echo "--------------------------------------------------------"
echo

# Remove previous running containers
echo "Removing existing opnfv/functest containers..."
docker ps | grep opnfv/functest | awk '{print $1}' | xargs docker stop &>/dev/null
docker ps -a | grep opnfv/functest | awk '{print $1}' | xargs docker rm &>/dev/null

# Remove existing images
echo "Removing existing opnfv/functest images..."
docker images | grep opnfv/functest | awk '{print $3}' | xargs docker rmi &>/dev/null




# Start the build
echo "Starting the opnfv/functest image build..."
cd $WORKSPACE/docker/
docker build -t opnfv/functest .


# list the images
echo "Available images are:"
docker images


if [ ${PUSH_IMAGE} == true ]; then
    echo "Starting the push of Functest Docker image."
    echo "--------------------------------------------------------"
    echo
    # Push to the Dockerhub repository
    docker push opnfv/functest

    #tag=$(calculate_tag)
    #echo "New tag to push: ${tag}"
    #docker push opnfv/functest:${tag}
fi
