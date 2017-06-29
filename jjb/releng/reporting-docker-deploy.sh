#!/bin/bash

function check() {

    # Verify hosted
    sleep 5
    cmd=`curl -s --head  --request GET http://testresults.opnfv.org/reporting2/reporting/index.html | grep '200 OK' > /dev/null`
    rc=$?
    echo $rc

    if [[ $rc == 0 ]]
    then
        return 0
    else
        return 1
    fi

}

echo "Getting contianer Id of the currently running one"
contId=$(sudo docker ps | grep "opnfv/reporting:latest" | awk '{print $1}')

echo "Pulling the latest image"
sudo docker pull opnfv/reporting:latest

echo "Deleting old containers of opnfv/reporting:old"
sudo docker ps -a | grep "opnfv/reporting" | grep "old" | awk '{print $1}' | xargs -r sudo docker rm -f

echo "Deleting old images of opnfv/reporting:latest"
sudo docker images | grep "opnfv/reporting" | grep "old" | awk '{print $3}' | xargs -r sudo docker rmi -f


if [[ -z "$contId" ]]
then
    echo "No running reporting container"

    echo "Removing stopped reporting containers in the previous iterations"
    sudo docker ps -f status=exited | grep "opnfv_reporting" | awk '{print $1}' | xargs -r sudo docker rm -f
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
    sudo docker tag "$currImgId" opnfv/reporting:old

    echo "Removing stopped reporting containers in the previous iteration"
    sudo docker ps -f status=exited | grep "opnfv_reporting" | awk '{print $1}' | xargs -r sudo docker rm -f

    echo "Renaming the running container name to opnfv_reporting as to identify it."
    sudo docker rename $contId opnfv_reporting

    echo "Stop the currently running container"
    sudo docker stop $contId
fi

echo "Running a container with the new image"
#Ask Morgan for this

if check; then
    echo "TestResults Reporting Hosted."
else
    echo "TestResults Reporting Hosting Failed"
    if [[ $(sudo docker images | grep "opnfv/reporting" | grep "old" | awk '{print $3}') ]]; then
        echo "Running old Image"
        #Ask Morgan for this
        exit 1
    fi
fi

# Echo Images and Containers
sudo docker images
sudo docker ps -a
