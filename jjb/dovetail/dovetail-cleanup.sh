#!/bin/bash
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

echo "Cleaning up docker containers/images..."
# Remove previous running containers if exist
if [[ ! -z $(docker ps -a | grep opnfv/dovetail) ]]; then
    echo "Removing existing opnfv/dovetail containers..."
    docker ps -a | grep opnfv/dovetail | awk '{print $1}' | xargs docker rm -f >$redirect
fi

# Remove existing images if exist
if [[ ! -z $(docker images | grep opnfv/dovetail) ]]; then
    echo "Docker images to remove:"
    docker images | head -1 && docker images | grep opnfv/dovetail
    image_tags=($(docker images | grep opnfv/dovetail | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        echo "Removing docker image opnfv/dovetail:$tag..."
        docker rmi opnfv/dovetail:$tag >$redirect
    done
fi
