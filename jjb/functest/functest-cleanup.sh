#!/bin/bash

[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

echo "Cleaning up docker containers/images..."
FUNCTEST_IMAGE=opnfv/functest
# Remove containers along with image opnfv/functest:<none>
dangling_images=($(docker images -f "dangling=true" | grep $FUNCTEST_IMAGE | awk '{print $1}'))
if [[ -n ${dangling_images} ]]; then
    echo "  Removing $FUNCTEST_IMAGE:<none> images and their containers..."
    for image_id in "${dangling_images[@]}"; do
        echo "      Removing image_id: $image_id and its containers"
        docker ps -a | grep $image_id | awk '{print $1}'| xargs docker rm -f >${redirect}
        docker rmi $image_id >${redirect}
    done
fi

# Remove previous running containers if exist
functest_containers=$(docker ps -a | grep $FUNCTEST_IMAGE | awk '{print $1}')
if [[ -n ${functest_containers} ]]; then
    echo "  Removing existing $FUNCTEST_IMAGE containers..."
    docker rm -f $functest_containers >${redirect}
fi

# Remove existing images if exist
if [[ $CLEAN_DOCKER_IMAGES == true ]]; then
    functest_image_tags=($(docker images | grep $FUNCTEST_IMAGE | awk '{print $2}'))
    if [[ -n ${functest_image_tags} ]]; then
        echo "  Docker images to be removed:" >${redirect}
        (docker images | head -1 && docker images | grep $FUNCTEST_IMAGE) >${redirect}
        for tag in "${functest_image_tags[@]}"; do
            echo "      Removing docker image $FUNCTEST_IMAGE:$tag..."
            docker rmi $FUNCTEST_IMAGE:$tag >${redirect}
        done
    fi
fi
