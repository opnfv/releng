#!/bin/bash
#  Licensed to the Apache Software Foundation (ASF) under one   *
#  or more contributor license agreements.  See the NOTICE file *
#  distributed with this work for additional information        *
#  regarding copyright ownership.  The ASF licenses this file   *
#  to you under the Apache License, Version 2.0 (the            *
#  "License"); you may not use this file except in compliance   *
#  with the License.  You may obtain a copy of the License at   *
#                                                               *
#    http://www.apache.org/licenses/LICENSE-2.0                 *
#                                                               *
#  Unless required by applicable law or agreed to in writing,   *
#  software distributed under the License is distributed on an  *
#  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY       *
#  KIND, either express or implied.  See the License for the    *
#  specific language governing permissions and limitations      *
#  under the License.                                           *

# Assigning Variables
command=$1
url=$2

function check() {

    # Verify hosted
    sleep 5
    cmd=`curl -s --head  --request GET ${url} | grep '200 OK' > /dev/null`
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
contId=$(sudo docker ps | grep "opnfv/testapi:latest" | awk '{print $1}')

echo "Pulling the latest image"
sudo docker pull opnfv/testapi:latest

echo "Deleting old containers of opnfv/testapi:old"
sudo docker ps -a | grep "opnfv/testapi" | grep "old" | awk '{print $1}' | xargs -r sudo docker rm -f

echo "Deleting old images of opnfv/testapi:latest"
sudo docker images | grep "opnfv/testapi" | grep "old" | awk '{print $3}' | xargs -r sudo docker rmi -f


if [[ -z "$contId" ]]
then
    echo "No running testapi container"

    echo "Removing stopped testapi containers in the previous iterations"
    sudo docker ps -f status=exited | grep "opnfv_testapi" | awk '{print $1}' | xargs -r sudo docker rm -f
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
fi

echo "Running a container with the new image"
$1:latest

if check; then
    echo "TestResults Hosted."
else
    echo "TestResults Hosting Failed"
    if [[ $(sudo docker images | grep "opnfv/testapi" | grep "old" | awk '{print $3}') ]]; then
        echo "Running old Image"
        $1:old
        exit 1
    fi
fi

# Echo Images and Containers
sudo docker images
sudo docker ps -a
