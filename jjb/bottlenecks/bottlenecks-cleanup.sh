#!/bin/bash
set -e
[[ $GERRIT_REFSPEC_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

BOTTLENECKS_IMAGE=opnfv/bottlenecks
echo "Bottlenecks: docker containers/images cleaning up"

dangling_images=($(docker images -f "dangling=true" | grep $BOTTLENECKS_IMAGE | awk '{print $3}'))
if [[ -n $dangling_images ]]; then
    echo "Removing $BOTTLENECKS_IMAGE:<none> dangling images and their containers"
    docker images | head -1 && docker images | grep $dangling_images
    for image_id in "${dangling_images[@]}"; do
        echo "Bottlenecks: Removing dangling image $image_id"
        docker rmi -f $image_id >${redirect}
    done
fi

for image_id in "${dangling_images[@]}"; do
    if [[ -n $(docker ps -a | grep $image_id) ]]; then
        echo "Bottlenecks: Removing containers associated with dangling image: $image_id"
        docker ps -a | head -1 && docker ps -a | grep $image_id
        docker ps -a | grep $image_id | awk '{print $1}'| xargs docker rm -f >${redirect}
    fi
done

if [[ -n $(docker ps -a | grep $BOTTLENECKS_IMAGE) ]]; then
    echo "Removing existing $BOTTLENECKS_IMAGE containers"
    docker ps -a | grep $BOTTLENECKS_IMAGE | awk '{print $1}' | xargs docker rm -f >$redirect
fi

if [[ -n $(docker images | grep $BOTTLENECKS_IMAGE) ]]; then
    echo "Bottlenecks: docker images to remove:"
    docker images | head -1 && docker images | grep $BOTTLENECKS_IMAGE
    image_tags=($(docker images | grep $BOTTLENECKS_IMAGE | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        echo "Removing docker image $BOTTLENECKS_IMAGE:$tag..."
        docker rmi $BOTTLENECKS_IMAGE:$tag >$redirect
    done
fi

echo "Yardstick: docker containers/images cleaning up"
YARDSTICK_IMAGE=opnfv/yardstick

dangling_images=($(docker images -f "dangling=true" | grep $YARDSTICK_IMAGE | awk '{print $3}'))
if [[ -n $dangling_images ]]; then
    echo "Removing $YARDSTICK_IMAGE:<none> dangling images and their containers"
    docker images | head -1 && docker images | grep $dangling_images
    for image_id in "${dangling_images[@]}"; do
        echo "Yardstick: Removing dangling image $image_id"
        docker rmi -f $image_id >${redirect}
    done
fi

for image_id in "${dangling_images[@]}"; do
    if [[ -n $(docker ps -a | grep $image_id) ]]; then
        echo "Yardstick: Removing containers associated with dangling image: $image_id"
        docker ps -a | head -1 && docker ps -a | grep $image_id
        docker ps -a | grep $image_id | awk '{print $1}'| xargs docker rm -f >${redirect}
    fi
done

if [[ -n $(docker ps -a | grep $YARDSTICK_IMAGE) ]]; then
    echo "Removing existing $YARDSTICK_IMAGE containers"
    docker ps -a | grep $YARDSTICK_IMAGE | awk '{print $1}' | xargs docker rm -f >$redirect
fi

if [[ -n $(docker images | grep $YARDSTICK_IMAGE) ]]; then
    echo "Yardstick: docker images to remove:"
    docker images | head -1 && docker images | grep $YARDSTICK_IMAGE
    image_tags=($(docker images | grep $YARDSTICK_IMAGE | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        echo "Removing docker image $YARDSTICK_IMAGE:$tag..."
        docker rmi $YARDSTICK_IMAGE:$tag >$redirect
    done
fi

echo "InfluxDB: docker containers/images cleaning up"
INFLUXDB_IMAGE=tutum/influxdb

dangling_images=($(docker images -f "dangling=true" | grep $INFLUXDB_IMAGE | awk '{print $3}'))
if [[ -n $dangling_images ]]; then
    echo "Removing $INFLUXDB_IMAGE:<none> dangling images and their containers"
    docker images | head -1 && docker images | grep $dangling_images
    for image_id in "${dangling_images[@]}"; do
        echo "InfluxDB: Removing dangling image $image_id"
        docker rmi -f $image_id >${redirect}
    done
fi

for image_id in "${dangling_images[@]}"; do
    if [[ -n $(docker ps -a | grep $image_id) ]]; then
        echo "InfluxDB: Removing containers associated with dangling image: $image_id"
        docker ps -a | head -1 && docker ps -a | grep $image_id
        docker ps -a | grep $image_id | awk '{print $1}'| xargs docker rm -f >${redirect}
    fi
done

if [[ -n $(docker ps -a | grep $INFLUXDB_IMAGE) ]]; then
    echo "Removing existing $INFLUXDB_IMAGE containers"
    docker ps -a | grep $INFLUXDB_IMAGE | awk '{print $1}' | xargs docker rm -f >$redirect
fi

if [[ -n $(docker images | grep $INFLUXDB_IMAGE) ]]; then
    echo "InfluxDB: docker images to remove:"
    docker images | head -1 && docker images | grep $INFLUXDB_IMAGE
    image_tags=($(docker images | grep $INFLUXDB_IMAGE | awk '{print $2}'))
    for tag in "${image_tags[@]}"; do
        echo "Removing docker image $INFLUXDB_IMAGE:$tag..."
        docker rmi $INFLUXDB_IMAGE:$tag >$redirect
    done
fi