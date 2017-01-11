#!/bin/bash

function check() {

    # Verify hosted
    sleep 5
    cmd=`curl -s --head  --request GET http://testresults.opnfv.org/test/swagger/spec | grep '200 OK' > /dev/null`
    rc=$?
    echo $rc

    if [[ $? == 0 ]]
    then
        echo "TestResults Hosted."
    else
        echo "Failed to host."
        sudo docker run -dti -p "8082:8000" -e "mongodb_url=mongodb://172.17.0.1:27017" -e "swagger_url=http://testresults.opnfv.org/test" opnfv/testapi:"$1"
        echo "Running old docker image only."
        exit 1
    fi

}

echo "Pulling the latest image"
sudo docker pull opnfv/testapi:latest

echo "Getting contianer Id of the currently running one"
contId=$(sudo docker ps | grep "opnfv/testapi" | awk '{print $1}')

if [[ -z "$contId" ]]
then
    echo "No running testapi container"

    echo "Removing all stopped testapi containers if any"
    sudo docker ps -f status=exited | grep "opnfv_testapi" | awk '{print $1}' | xargs -r sudo docker rm -f

    if [[ ! -z $(netstat -antu | grep '8082') ]]
    then
        echo "Port 8082 is not free"
        exit 1
    fi

    echo "Running a container with the new image"
    sudo docker run -dti -p "8082:8000" -e "mongodb_url=mongodb://172.17.0.1:27017" -e "swagger_url=http://testresults.opnfv.org/test" opnfv/testapi:latest
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

    echo "Removing all stopped containers if any"
    sudo docker ps -f status=exited | grep "opnfv_testapi" | awk '{print $1}' | xargs -r sudo docker rm -f

    echo "Stop all runnning testapi containers"
    sudo docker ps | grep "opnfv/testapi" | awk '{ print $1 }' | xargs -r sudo docker stop

    echo "Removing all testapi images before the currently running ones"
    sudo docker images -f before="$currImgId" | grep "opnfv/testapi" | awk '{print $3}' | xargs -r sudo docker rmi -f

    echo "Renaming the running container name to opnfv_testapi as to identify it."
    sudo docker rename $contId opnfv_testapi

    echo "Stop the currently running container"
    sudo docker stop $contId

    if [[ ! -z $(netstat -antu | grep '8082') ]]
    then
        echo "Port 8082 is not free"
        exit 1
    fi

    echo "Running a container with the new image"
    sudo docker run -dti -p "8082:8000" -e "mongodb_url=mongodb://172.17.0.1:27017" -e "swagger_url=http://testresults.opnfv.org/test" opnfv/testapi:latest
    check old
fi

sudo docker images
sudo docker ps