#!/bin/bash
##############################################################################
# Copyright (c) 2018 Huawei and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

info ()  {
    logger -s -t "fetch_k8_conf.info" "$*"
}


error () {
    logger -s -t "fetch_k8_conf.error" "$*"
    exit 1
}

: ${DEPLOY_TYPE:=''}

#Get options
while getopts ":d:i:a:h:s:o:v" optchar; do
    case "${optchar}" in
        d) dest_path=${OPTARG} ;;
        i) installer_type=${OPTARG} ;;
        v) DEPLOY_TYPE="virt" ;;
        *) echo "Non-option argument: '-${OPTARG}'" >&2
           usage
           exit 2
           ;;
    esac
done

# set vars from env if not provided by user as options
dest_path=${dest_path:-$HOME/admin.conf}
installer_type=${installer_type:-$INSTALLER_TYPE}

if [ -z $dest_path ] || [ -z $installer_type ]; then
    usage
    exit 2
fi

# Checking if destination path is valid
if [ -d $dest_path ]; then
    error "Please provide the full destination path for the credentials file including the filename"
else
    # Check if we can create the file (e.g. path is correct)
    touch $dest_path || error "Cannot create the file specified. Check that the path is correct and run the script again."
fi

if [ "$installer_type" == "compass" ]; then
    info "Fetching admin.conf file on Compass"
    sudo docker cp compass-tasks:/opt/admin.conf $dest_path &> /dev/null
    sudo chown $(whoami):$(whoami) $dest_path
    info "Fetch admin.conf successfully"
elif [ "$installer_type" == "joid" ]; then
    info "Do nothing, config file has been provided in $HOME/joid_config/config for joid"
elif [ "$installer_type" == "fuel" ]; then
    info "Getting kubernetes config ..."
    docker cp fuel:/opt/kubernetes.config $dest_path
else
    error "Installer $installer_type is not supported by this script"
fi

