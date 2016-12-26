#!/bin/bash

[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

#clean up dovetail and its dependent project docker images with tag None
clean_images=(opnfv/dovetail opnfv/functest opnfv/yardstick)
for clean_image in "${clean_images[@]}"; do
    echo "Remove containers with image ${clean_image}:<None>..."
    dangling_images=($(docker images -qf "dangling=true" | grep ${clean_image} | awk '{print $3}'))
    if [[ -n ${dangling_images} ]]; then
        echo "Removing ${clean_image}:<none> images and their containers..."
        for image_id in "${dangling_images[@]}"; do
            echo "Removing image_id: $image_id and its containers"
            docker ps -a | grep $image_id | awk '{print $1}'| xargs docker rm -f >${redirect}
            docker rmi $image_id >${redirect}
        done
    fi
done

echo "Cleaning up dovetail docker containers/images..."
if [[ ! -z $(docker ps -a | grep opnfv/dovetail) ]]; then
    echo "Removing existing opnfv/dovetail containers..."
    docker ps -a | grep opnfv/dovetail | awk '{print $1}' | xargs docker rm -f >${redirect}
fi

echo "Remove dovetail existing images if exist..."
if [[ ! -z $(docker images | grep opnfv/dovetail) ]]; then
    echo "Docker images to remove:"
    docker images | head -1 && docker images | grep opnfv/dovetail >${redirect}
    image_tags=($(docker images | grep opnfv/dovetail | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        echo "Removing docker image opnfv/dovetail:$tag..."
        docker rmi opnfv/dovetail:$tag >${redirect}
    done
fi
