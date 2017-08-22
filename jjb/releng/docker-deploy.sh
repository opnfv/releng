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


command=$1
url=$2
module=$3

REPO="opnfv"
latest_image=$REPO/$module:latest
old_image=$REPO/$module:old
latest_container_name=$module
old_container_name=$module"_old"
latest_container_id=
old_container_id=
new_start_container=

function DEBUG() {
  echo `date "+%Y-%m-%d %H:%M:%S.%N"` ": $1"
}

function check_connectivity() {
    # check update status via test the connectivity of provide url
    sleep 5
    cmd=`curl -s --head  --request GET ${url} | grep '200 OK' > /dev/null`
    rc=$?
    DEBUG $rc
    if [[ $rc == 0 ]]; then
        return 0
    else
        return 1
    fi
}


function pull_latest_image() {
    DEBUG "pull latest image $latest_image"
    docker pull $latest_image
}

function get_latest_running_container() {
    latest_container_id=`docker ps -q --filter name=^/$latest_container_name$`
}

function get_old_running_container() {
    old_container_id=`docker ps -q --filter name=^/$old_container_name$`
}

function delete_old_image() {
    DEBUG "delete old image: $old_image"
    docker rmi -f $old_image
}

function delete_old_container() {
    DEBUG "delete old container: $old_container_name"
    docker ps -a -q --filter name=^/$old_container_name$ | xargs docker rm -f &>/dev/null
}

function delete_latest_container() {
    DEBUG "delete latest container: $module"
    docker ps -a -q --filter name=^/$latest_container_name$ | xargs docker rm -f &>/dev/null
}

function delete_latest_image() {
    DEBUG "delete latest image: $REPO/$module:latest"
    docker rmi -f $latest_image
}

function change_image_tag_2_old() {
    DEBUG "change image tag 2 old"
    docker tag $latest_image $old_image
    docker rmi -f $latest_image
}

function mark_latest_container_2_old() {
    DEBUG "mark latest container to be old"
    docker rename "$latest_container_name" "$old_container_name"
}

function stop_old_container() {
    DEBUG "stop old container"
    docker stop "$old_container_name"
}

function run_latest_image() {
    new_start_container=`$command`
    DEBUG "run latest image: $new_start_container"
}

get_latest_running_container
get_old_running_container

if [[ ! -z $latest_container_id ]]; then
    DEBUG "latest container is running: $latest_container_id"
    delete_old_container
    delete_old_image
    change_image_tag_2_old
    mark_latest_container_2_old
    pull_latest_image
    stop_old_container
    run_latest_image

elif [[ ! -z $old_container_id ]]; then
    DEBUG "old container is running: $old_container_id"
    delete_latest_container
    delete_latest_image
    pull_latest_image
    stop_old_container
    run_latest_image
else
    DEBUG "no container is running"
    delete_old_container
    delete_old_image
    delete_latest_container
    delete_latest_image
    pull_latest_image
    run_latest_image
fi

if check_connectivity; then
    DEBUG "CONGRATS: $module update successfully"
else
    DEBUG "ATTENTION: $module update failed"
    id=`docker ps -a -q --filter name=^/$old_container_name$`
    if [[ ! -z $id ]]; then
        DEBUG "start old container instead"
        docker stop $new_start_container
        docker start $id
    fi
    if ! check_connectivity; then
        DEBUG "BIG ISSUE: no container is running normally"
    fi
    exit 1
fi

docker images
docker ps -a
