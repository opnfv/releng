#!/bin/bash
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

echo "Cleaning up docker containers/images..."
# Remove previous running containers if exist
if [[ ! -z $(docker ps -a | grep opnfv/yardstick) ]]; then
    echo "Removing existing opnfv/yardstick containers..."
    docker ps -a | grep opnfv/yardstick | awk '{print $1}' | xargs docker rm -f >$redirect

fi

# Remove existing images if exist
if [[ ! -z $(docker images | grep opnfv/yardstick) ]]; then
    echo "Docker images to remove:"
    docker images | head -1 && docker images | grep opnfv/yardstick
    image_tags=($(docker images | grep opnfv/yardstick | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        echo "Removing docker image opnfv/yardstick:$tag..."
        docker rmi opnfv/yardstick:$tag >$redirect

    done
fi
