#!/bin/bash

[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

echo "Cleaning up docker containers/images..."

# Remove containers along with image opnfv/functest:<none>
images_dangling=($(docker images -q -f "dangling=true"))
if [[ -n ${images_dangling} ]]; then
    echo "Removing image opnfv:functest:<none> and its containers..."
    for image_id in "${images_dangling[@]}"; do
        docker ps -a | grep $image_id | awk '{print $1}'| xargs docker rm -f >${redirect}
        docker rmi $image_id >${redirect}
    done
fi

# Remove previous running containers if exist
if [[ ! -z $(docker ps -a | grep opnfv/functest) ]]; then
    echo "Removing existing opnfv/functest containers..."
    docker ps -a | grep opnfv/functest | awk '{print $1}' | xargs docker rm -f >${redirect}
fi

# Remove existing images if exist
if [[ $CLEAN_DOCKER_IMAGES == true ]] && [[ ! -z $(docker images | grep opnfv/functest) ]]; then
    echo "Docker images to remove:"
    (docker images | head -1 && docker images | grep opnfv/functest) >${redirect}
    image_tags=($(docker images | grep opnfv/functest | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        echo "Removing docker image opnfv/functest:$tag..."
        docker rmi opnfv/functest:$tag >${redirect}
    done
fi
