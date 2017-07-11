#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
#           (c) 2017 Enea AB
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o pipefail

# disable Fuel ISO download for master branch
[[ "$BRANCH" == 'master' ]] && exit 0

echo "Host info: $(hostname) $(hostname -I)"

# Configurable environment variables:
# ISOSTORE (/iso_mount/opnfv_ci)

if [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Downloading http://$GS_URL/opnfv-gerrit-$GERRIT_CHANGE_NUMBER.properties"
    # get the properties file for the Armband Fuel ISO built for a merged change
    curl -f -s -o $WORKSPACE/latest.properties http://$GS_URL/opnfv-gerrit-$GERRIT_CHANGE_NUMBER.properties
else
    # get the latest.properties file in order to get info regarding latest artifact
    echo "Downloading http://$GS_URL/latest.properties"
    curl -f -s -o $WORKSPACE/latest.properties http://$GS_URL/latest.properties
fi

# source the file so we get artifact metadata, it will exit if it doesn't exist
source latest.properties

# echo the info about artifact that is used during the deployment
OPNFV_ARTIFACT=${OPNFV_ARTIFACT_URL/*\/}
echo "Using $OPNFV_ARTIFACT for deployment"

# Releng doesn't want us to use anything but opnfv.iso for now. We comply.
ISO_FILE=${WORKSPACE}/opnfv.iso

# using ISOs for verify & merge jobs from local storage will be enabled later
if [[ ! "$JOB_NAME" =~ (verify|merge) ]]; then
    # check if we already have the ISO to avoid redownload
    ISOSTORE=${ISOSTORE:-/iso_mount/opnfv_ci}/${BRANCH##*/}
    if [[ -f "$ISOSTORE/$OPNFV_ARTIFACT" ]]; then
        echo "ISO exists locally. Skipping the download and using the file from ISO store"
        ln -s $ISOSTORE/$OPNFV_ARTIFACT ${ISO_FILE}
        echo "--------------------------------------------------------"
        echo
        ls -al ${ISO_FILE}
        echo
        echo "--------------------------------------------------------"
        echo "Done!"
        exit 0
    fi
fi

# Use gsutils if available
if $(which gsutil &>/dev/null); then
    DOWNLOAD_URL="gs://$OPNFV_ARTIFACT_URL"
    CMD="gsutil cp ${DOWNLOAD_URL} ${ISO_FILE}"
else
    # download image
    # -f returns error if the file was not found or on server error
    DOWNLOAD_URL="http://$OPNFV_ARTIFACT_URL"
    CMD="curl -f -s -o ${ISO_FILE} ${DOWNLOAD_URL}"
fi

# log info to console
echo "Downloading the $INSTALLER_TYPE artifact using URL $DOWNLOAD_URL"
echo "This could take some time..."
echo "--------------------------------------------------------"
echo "$CMD"
$CMD
echo "--------------------------------------------------------"
echo "Done!"
