#!/bin/bash
[[ ${CI_DEBUG} == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

# Remove containers along with image opnfv/yardstick*:<none>
dangling_images=($(docker images -f "dangling=true" | awk '/opnfv[/]yardstick/ {print $3}'))
if [[ ${#dangling_images[@]} -eq 0 ]] ; then
    echo "Removing opnfv/yardstick:<none> images and their containers..."
    for image_id in "${dangling_images[@]}"; do
        echo "      Removing image_id: $image_id and its containers"
        containers=$(docker ps -a | awk "/${image_id}/ {print \$1}")
        if [[ -n "$containers" ]];then
            docker rm -f "${containers}" >${redirect}
        fi
        docker rmi "${image_id}" >${redirect}
    done
fi

echo "Cleaning up docker containers/images..."
# Remove previous running containers if exist
if docker ps -a | grep -q opnfv/yardstick; then
    echo "Removing existing opnfv/yardstick containers..."
    docker ps -a | awk "/${image_id}/ {print \$1}" | xargs docker rm -f >${redirect}

fi

# Remove existing images if exist
if docker images | grep -q opnfv/yardstick; then
    echo "Docker images to remove:"
    docker images | head -1 && docker images | grep opnfv/yardstick
    image_ids=($(docker images | awk '/opnfv[/]yardstick/ {print $3}'))
    for id in "${image_ids[@]}"; do
        echo "Removing docker image id $id..."
        if ! docker rmi "${id}" >${redirect} ; then
            echo "Some kind of docker remove failure, ignoring"
        fi
    done
fi

