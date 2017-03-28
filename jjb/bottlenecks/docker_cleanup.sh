#!/bin/bash
##############################################################################
# Copyright (c) 2017 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

usage="Script to clear up dockers and their images.

usage:
    bash $(basename "$0") [-h|--help] [-d|--docker <docker name>] [--debug]

where:
    -h|--help         show the help text
    -d|--docker       specify dockers' name
      <docker name>   keyword of dockers' name used to find dockers
                          e.g. keyword "bottlenecks" to find "opnfv/bottlenecks:*"
    --debug           print debug information with default false

examples:
    $(basename "$0")
    $(basename "$0") -d bottlenecks --debug"

clnup_debug=false

while [[ $#>0 ]]; do
    clnup_docr="$1"
    case $clnup_docr in
        -h|--help)
            echo "$usage"
            exit 0
            shift
        ;;
        -d|--docker)
            docker_name="$2"
            shift

            if [[ $2 == "--debug" ]]; then
                clnup_debug=true
                shift
            fi
        ;;
        --debug)
            clnup_debug=true
            shift
            if [[ "$1" == "-d" || "$1" == "--docker" ]]; then
                docker_name="$2"
                shift
            fi
        ;;
        *)
            echo "unknow options $1 $2 $3"
            exit 1
        ;;
    esac
    shift
done


# check if docker name is empty
if [[ $docker_name == "" ]]; then
    echo empty docker name
    exit 1
fi

# clean up dockers and their images with keyword in their names
[[ $clnup_debug == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

echo "$docker_name: docker containers/images cleaning up"

dangling_images=($(docker images -f "dangling=true" | grep $docker_name | awk '{print $3}'))
if [[ -n $dangling_images ]]; then
    echo "Removing $docker_name:<none> dangling images and their containers"
    docker images | head -1 && docker images | grep $dangling_images
    for image_id in "${dangling_images[@]}"; do
        echo "$docker_name: Removing dangling image $image_id"
        docker rmi -f $image_id >${redirect}
    done
fi

for image_id in "${dangling_images[@]}"; do
    if [[ -n $(docker ps -a | grep $image_id) ]]; then
        echo "$docker_name: Removing containers associated with dangling image: $image_id"
        docker ps -a | head -1 && docker ps -a | grep $image_id
        docker ps -a | grep $image_id | awk '{print $1}'| xargs docker rm -f >${redirect}
    fi
done

if [[ -n $(docker ps -a | grep $docker_name) ]]; then
    echo "Removing existing $docker_name containers"
    docker ps -a | head -1 && docker ps -a | grep $docker_name
    docker ps -a | grep $docker_name | awk '{print $1}' | xargs docker rm -f >$redirect
fi

if [[ -n $(docker images | grep $docker_name) ]]; then
    echo "$docker_name: docker images to remove:"
    docker images | head -1 && docker images | grep $docker_name
    image_ids=($(docker images | grep $docker_name | awk '{print $3}'))
    for image_id in "${image_ids[@]}"; do
        echo "Removing docker image $docker_name:$tag..."
        docker rmi $image_id >$redirect
    done
fi
