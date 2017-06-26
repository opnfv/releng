#!/bin/bash
##############################################################################
# Copyright (c) 2017 Huawei Technologies Co.,Ltd and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

# clean up dependent project docker images, which has no containers and image tag None
clean_images=(opnfv/functest opnfv/yardstick opnfv/testapi mongo)
for clean_image in "${clean_images[@]}"; do
    echo "Removing image $image_id, which has no containers and image tag is None"
    dangling_images=($(docker images -f "dangling=true" | grep ${clean_image} | awk '{print $3}'))
    if [[ -n ${dangling_images} ]]; then
        for image_id in "${dangling_images[@]}"; do
            docker rmi $image_id >${redirect}
        done
    fi
done

echo "Remove containers with image opnfv/dovetail:<None>..."
dangling_images=($(docker images -f "dangling=true" | grep opnfv/dovetail | awk '{print $3}'))
if [[ -n ${dangling_images} ]]; then
    for image_id in "${dangling_images[@]}"; do
        echo "Removing image $image_id with tag None and its related containers"
        docker ps -a | grep $image_id | awk '{print $1}'| xargs docker rm -f >${redirect}
        docker rmi $image_id >${redirect}
    done
fi

echo "Cleaning up dovetail docker containers..."
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
