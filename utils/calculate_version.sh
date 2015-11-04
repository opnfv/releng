#!/bin/bash

#
# Authors:
#      Jose Lausuch <jose.lausuch@ericsson.com>
#      Fatih Degirmenci <fatih.degirmenci@ericsson.com>
#
# Calculates and generates the version tag for the OPNFV objects:
#     - Docker images
#     - ISOs
#     - Artifcats
#

usage="Calculates the version text of one of the following objects.

usage:
    bash $(basename "$0") [-h|--help] -t|--type docker|iso|artifact -i|--info <additional info>

where:
    -h|--help      show this help text
    -t|--type      specify the type of object you want the version from
    -i|--info       additional info of the object type

examples:
    $(basename "$0") -t docker opnfv/functest
    $(basename "$0") -t iso fuel"


info ()  {
    logger -s -t "Calculate_version.info" "$*"
}


error () {
    logger -s -t "Calculate_version.error" "$*"
    exit 1
}

ARR_TYPES=(docker iso artifact)
TYPE=""
INFO=""
RELEASE_NAME="brahmaputra"

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
        -i|--info)
            INFO="$2"
            shift
        ;;
        *)
            error "unknown option $1"
            exit 1
        ;;
    esac
    shift # past argument or value
done



if [ "${TYPE}" == "" ]; then
    error "Please specify the type of object to get the version from. $usage"
fi

if [ "${INFO}" == "" ]; then
    error "Please specify the additional info for the given object type. $usage"
fi

not_in=1
for i in "${ARR_TYPES[@]}"; do
    if [[ "${TYPE}" == "$i" ]]; then
        not_in=0
    fi
done
if [ ${not_in} == 1 ]; then
    error "Unknown type: ${TYPE}. Available object types are: [${ARR_TYPES[@]}]"
fi


#Functions which calculate the version text
function docker_version() {
    docker_image=$1
    url_repo="https://registry.hub.docker.com/v2/repositories/${docker_image}/"
    url_tag="https://registry.hub.docker.com/v2/repositories/${docker_image}/tags/"
    status=$(curl -s --head -w %{http_code} ${url_repo} -o /dev/null)
    if [ "${status}" != "200" ]; then
        error "Cannot access ${url_repo}. Does the image ${docker_image} exist?"
    fi
    tag_json=$(curl $url_tag 2>/dev/null | python -mjson.tool | grep ${RELEASE_NAME} | head -1)
    if [ "${tag_json}" == "" ]; then
        error "The Docker Image ${docker_image} does not have a TAG ${RELEASE_NAME}"
    fi
    tag=$(echo $tag_json | awk '{print $2}' | sed 's/\,//' | sed 's/\"//g')
    #ex: tag=brahmaputra.2016.0.2
    tag_arr=(${tag//./ })
    tag_release_name=${tag_arr[0]}
    tag_year=${tag_arr[1]}
    tag_release=${tag_arr[2]}
    tag_version=${tag_arr[3]}
    tag_version_new=$(($tag_version+1))
    tag_new=${tag_release_name}.${tag_year}.${tag_release}.${tag_version_new}
    echo $tag_new
}

function iso_version() {
    info "To be done"
}

function artifact_version() {
    info "To be done"
}

#info "Calculating version for object '${TYPE}' with arguments '${INFO}'..."
if [ "${TYPE}" == "docker" ]; then
    docker_version $INFO
elif [ "${TYPE}" == "iso" ]; then
    iso_version $INFO
elif [ "${TYPE}" == "docker" ]; then
    artifact_version $INFO
fi


