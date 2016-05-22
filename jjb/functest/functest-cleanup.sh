#!/bin/bash

[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

echo "Cleaning up docker containers/images..."
# Remove previous running containers if exist
if [[ ! -z $(docker ps -a | grep opnfv/functest) ]]; then
    echo "Removing existing opnfv/functest containers..."
    docker ps -a | grep opnfv/functest | awk '{print $1}' | xargs docker rm -f >${redirect}
fi

# Remove existing images if exist
if [[ ! -z $(docker images | grep opnfv/functest) ]]; then
    echo "Docker images to remove:"
    docker images | head -1 && docker images | grep opnfv/functest >${redirect}
    image_tags=($(docker images | grep opnfv/functest | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        echo "Removing docker image opnfv/functest:$tag..."
        docker rmi opnfv/functest:$tag >/dev/null
    done
fi
