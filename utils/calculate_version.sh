#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# Calculates and generates the version tag for the OPNFV objects:
#     - Docker images
#     - ISOs
#     - Artifacts

info ()  {
    logger -s -t "Calculate_version.info" "$*"
}


error () {
    logger -s -t "Calculate_version.error" "$*"
    exit 1
}


#Functions which calculate the version
function docker_version() {
    docker_image=$1
    url_repo="https://registry.hub.docker.com/v2/repositories/${docker_image}/"
    url_tag="https://registry.hub.docker.com/v2/repositories/${docker_image}/tags/"
    status=$(curl -s --head -w %{http_code} ${url_repo} -o /dev/null)
    if [ "${status}" != "200" ]; then
        error "Cannot access ${url_repo}. Does the image ${docker_image} exist?"
    fi
    tag_json=$(curl $url_tag 2>/dev/null | python -mjson.tool | grep ${BASE_VERSION} | head -1)
    #e.g. tag_json= "name": "brahmaputra.0.2",
    #for dovetail, not sync with release, tag_json= "name": "dovetail.1.0"
    if [ "${tag_json}" == "" ]; then
        echo ${BASE_VERSION}.0
    else
        tag=$(echo $tag_json | awk '{print $2}' | sed 's/\,//' | sed 's/\"//g')
        #e.g.: tag=brahmaputra.0.2
        #for dovetail, not sync with release, e.g.: tag=dovetail.1.0
        tag_current_version=$(echo $tag | sed 's/.*\.//')
        tag_new_version=$(($tag_current_version+1))
        #e.g.: tag=brahmaputra.0.3
        echo ${BASE_VERSION}.${tag_new_version}
    fi
}


function artifact_version() {
    # To be done
    error "Not supported yet..."
}


STORAGE_TYPES=(docker artifactrepo)
TYPE=""
NAME=""


usage="Calculates the version text of one of the following objects.

usage:
    bash $(basename "$0") [-h|--help] -t|--type docker|artifactrepo -n|--name <object_name>

where:
    -h|--help      show this help text
    -t|--type      specify the storage location
    -n|--name      name of the repository/object

examples:
    $(basename "$0") -t docker -n opnfv/functest
    $(basename "$0") -t artifactrepo -n fuel"




# Parse parameters
while [[ $# > 0 ]]
    do
    key="$1"
    case $key in
        -h|--help)
            echo "$usage"
            exit 0
            shift
        ;;
        -t|--type)
            TYPE="$2"
            shift
        ;;
        -n|--name)
            NAME="$2"
            shift
        ;;
        *)
            error "unknown option $1"
            exit 1
        ;;
    esac
    shift # past argument or value
done

if [ -z "$BASE_VERSION" ]; then
    error "Base version must be specified as environment variable. Ex.: export BASE_VERSION='brahmaputra.0'"
fi

if [ "${TYPE}" == "" ]; then
    error "Please specify the type of object to get the version from. $usage"
fi

if [ "${NAME}" == "" ]; then
    error "Please specify the name for the given storage type. $usage"
fi

not_in=1
for i in "${STORAGE_TYPES[@]}"; do
    if [[ "${TYPE}" == "$i" ]]; then
        not_in=0
    fi
done
if [ ${not_in} == 1 ]; then
    error "Unknown type: ${TYPE}. Available storage types are: [${STORAGE_TYPES[@]}]"
fi


#info "Calculating version for object '${TYPE}' with arguments '${INFO}'..."
if [ "${TYPE}" == "docker" ]; then
    docker_version $NAME

elif [ "${TYPE}" == "artifactrepo" ]; then
    artifact_version $NAME
fi
