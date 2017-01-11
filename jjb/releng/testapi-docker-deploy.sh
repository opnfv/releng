#!/bin/bash

function check() {

    # Verify hosted
    sleep 5
    cmd=`curl -s --head  --request GET http://testresults.opnfv.org/auto/swagger/spec | grep '200 OK' > /dev/null`
    rc=$?
    echo $rc

    if [[ $? == 0 ]]
    then
        echo "TestResults Hosted."
    else
        echo "Failed to host."
        sudo docker run -dti -p "8711:8000" -e "mongodb_url=mongodb://172.17.0.1:27017" -e "swagger_url=http://testresults.opnfv.org/auto" opnfv/testapi:"$1"
        echo "Running old docker image only."
        exit 1
    fi

}

echo "Getting contianer Id of the currently running one"
contId=$(sudo docker ps | grep "opnfv/testapi:latest" | awk '{print $1}')

echo "Pulling the latest image"
sudo docker pull opnfv/testapi:latest

echo "Deleting old images of opnfv/testapi:latest"
sudo docker images | grep "opnfv/testapi:old" | awk '{print $3}' | xargs -r sudo docker rmi -f


if [[ -z "$contId" ]]
then
    echo "No running testapi container"

    echo "Removing stopped testapi containers in the previous iterations"
    sudo docker ps -f status=exited | grep "opnfv_testapi" | awk '{print $1}' | xargs -r sudo docker rm -f

    echo "Running a container with the new image"
    sudo docker run -dti -p "8711:8000" -e "mongodb_url=mongodb://172.17.0.1:27017" -e "swagger_url=http://testresults.opnfv.org/auto" opnfv/testapi:"$1"
    check latest
else
    echo $contId

    echo "Get the image id of the currently running conatiner"
    currImgId=$(sudo docker ps | grep "$contId" | awk '{print $2}')
    echo $currImgId

    if [[ -z "$currImgId" ]]
    then
        echo "No image id found for the container id"
        exit 1
    fi

    echo "Changing current image tag to old"
    sudo docker tag "$currImgId" opnfv/testapi:old

    echo "Removing stopped testapi containers in the previous iteration"
    sudo docker ps -f status=exited | grep "opnfv_testapi" | awk '{print $1}' | xargs -r sudo docker rm -f

    echo "Renaming the running container name to opnfv_testapi as to identify it."
    sudo docker rename $contId opnfv_testapi

    echo "Stop the currently running container"
    sudo docker stop $contId

    echo "Running a container with the new image"
    sudo docker run -dti -p "8711:8000" -e "mongodb_url=mongodb://172.17.0.1:27017" -e "swagger_url=http://testresults.opnfv.org/auto" opnfv/testapi:latest
    check old
fi

sudo docker images
sudo docker ps -a
