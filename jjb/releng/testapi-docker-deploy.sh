#!/bin/bash

set -o errexit

# Ssh into the machine
ssh -T -oStrictHostKeyChecking=no jenkins@testresults.opnfv.org 'bash -s' << 'EOSSH'

echo "Getting contianer Id of the currently running one"
contId=$(sudo docker ps | grep "opnfv/testapi" | awk '{print $1}')

if [[ -z "$contId" ]]
then
    echo "No running testapi container"

    echo "Pulling the latest image"
    sudo docker pull opnfv/testapi:latest

    echo "Removing all stopped containers if any"
    sudo docker ps -f status=exited -q | grep "opnfv/testapi" | xargs -r sudo docker rm -f

    if [[ ! -z $(netstat -antu | grep '8000') ]]
    then
        echo "Port 8000 is not free"
        exit 1
    fi
    echo "Running a container with the new image"
    sudo docker run -dti -p 8000:8000 opnfv/testapi:latest
else
    echo $contId

    echo "Pulling the latest image"
    sudo docker pull opnfv/testapi:latest

    echo "Get the image id of the currently running conatiner"
    currImgId=$(sudo docker ps | grep "$contId" | awk '{print $2}')
    echo $currImgId

    if [[ -z "$currImgId" ]]
    then
        echo "No image id found for the container id"
        exit 1
    fi

    echo "Changing current image tag to stable"
    sudo docker tag "$currImgId" opnfv/testapi:stable

    echo "Removing all stopped containers if any"
    sudo docker ps -f status=exited -q | xargs -r sudo docker rm -f

    echo "Stop all runnning testapi containers"
    sudo docker ps | grep "opnfv/testapi" | awk '{ print $1 }' | xargs -r sudo docker stop

    echo "Removing all testapi images before the currently running ones"
    sudo docker images -f before="$currImgId" | grep "opnfv/testapi" | awk '{print $3}' | xargs -r sudo docker rmi -f

    echo "Stop the currently running container"
    sudo docker stop $contId

    if [[ ! -z $(netstat -antu | grep '8000') ]]
    then
        echo "Port 8000 is not free"
        exit 1
    fi
    echo "Running a container with the new image"
    sudo docker run -dti -p 8000:8000 opnfv/testapi:latest
fi

sudo docker images
sudo docker ps

EOSSH
