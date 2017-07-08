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
module=$3

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
contId=$(sudo docker ps | grep "opnfv/${module}:latest" | awk '{print $1}')

echo $contId

echo "Pulling the latest image"
sudo docker pull opnfv/${module}:latest

echo "Deleting old containers of opnfv/${module}:old"
sudo docker ps -a | grep "opnfv/${module}" | grep "old" | awk '{print $1}' | xargs -r sudo docker rm -f

echo "Deleting old images of opnfv/${module}:latest"
sudo docker images | grep "opnfv/${module}" | grep "old" | awk '{print $3}' | xargs -r sudo docker rmi -f


if [[ -z "$contId" ]]
then
    echo "No running ${module} container"

    echo "Removing stopped ${module} containers in the previous iterations"
    sudo docker ps -f status=exited | grep "opnfv_${module}" | awk '{print $1}' | xargs -r sudo docker rm -f
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
    sudo docker tag "$currImgId" opnfv/${module}:old

    echo "Removing stopped ${module} containers in the previous iteration"
    sudo docker ps -f status=exited | grep "opnfv_${module}" | awk '{print $1}' | xargs -r sudo docker rm -f

    echo "Renaming the running container name to opnfv_${module} as to identify it."
    sudo docker rename $contId opnfv_${module}

    echo "Stop the currently running container"
    sudo docker stop $contId
fi

echo "Running a container with the new image"
$command:latest

if check; then
    echo "TestResults Module Hosted."
else
    echo "TestResults Module Failed"
    if [[ $(sudo docker images | grep "opnfv/${module}" | grep "old" | awk '{print $3}') ]]; then
        echo "Running old Image"
        $command:old
        exit 1
    fi
fi

# Echo Images and Containers
sudo docker images
sudo docker ps -a
