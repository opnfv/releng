#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o pipefail

if [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Downloading http://$GS_URL/opnfv-gerrit-$GERRIT_CHANGE_NUMBER.properties"
    # get the properties file for the Armband Fuel ISO built for a merged change
    curl -s -o $WORKSPACE/latest.properties http://$GS_URL/opnfv-gerrit-$GERRIT_CHANGE_NUMBER.properties
else
    # get the latest.properties file in order to get info regarding latest artifact
    echo "Downloading http://$GS_URL/latest.properties"
    curl -s -o $WORKSPACE/latest.properties http://$GS_URL/latest.properties
fi

# check if we got the file
# FIXME: the file is created even if it didn't exist on the host
#        We should check that the contents are sane
[[ -f latest.properties ]] || exit 1

# source the file so we get artifact metadata
source latest.properties

# echo the info about artifact that is used during the deployment
OPNFV_ARTIFACT=${OPNFV_ARTIFACT_URL/*\/}
echo "Using $OPNFV_ARTIFACT for deployment"

# using ISOs for verify & merge jobs from local storage will be enabled later
if [[ ! "$JOB_NAME" =~ (verify|merge) ]]; then
    # check if we already have the ISO to avoid redownload
    ISOSTORE="/iso_mount/opnfv_ci/${GIT_BRANCH##*/}"
    if [[ -f "$ISOSTORE/$OPNFV_ARTIFACT" ]]; then
        echo "ISO exists locally. Skipping the download and using the file from ISO store"
        ln -s $ISOSTORE/$OPNFV_ARTIFACT $WORKSPACE/opnfv.iso
        echo "--------------------------------------------------------"
        echo
        ls -al $WORKSPACE/opnfv.iso
        echo
        echo "--------------------------------------------------------"
        echo "Done!"
        exit 0
    fi
fi

# log info to console
echo "Downloading the $INSTALLER_TYPE artifact using URL http://$OPNFV_ARTIFACT_URL"
echo "This could take some time..."
echo "--------------------------------------------------------"
echo

# download the file
curl -s -o $WORKSPACE/opnfv.iso http://$OPNFV_ARTIFACT_URL

# The file is always created, check that it is in fact an ISO image
[[ $(file $WORKSPACE/opnfv.iso) =~ ISO ]]

echo
echo "--------------------------------------------------------"
echo "Done!"
