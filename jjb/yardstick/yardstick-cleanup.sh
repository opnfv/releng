#!/bin/bash
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

# Remove containers along with image opnfv/yardstick*:<none>
dangling_images=($(docker images -f "dangling=true" | grep opnfv/yardstick | awk '{print $3}'))
if [[ -n ${dangling_images} ]]; then
    echo "Removing opnfv/yardstick:<none> images and their containers..."
    for image_id in "${dangling_images[@]}"; do
        echo "      Removing image_id: $image_id and its containers"
        containers=$(docker ps -a | grep $image_id | awk '{print $1}')
        if [[ -n "$containers" ]];then
            docker rm -f $containers >${redirect}
        fi
        docker rmi $image_id >${redirect}
    done
fi

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

