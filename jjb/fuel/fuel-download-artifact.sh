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
set -o nounset
set -o pipefail

if [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Downloading http://$GS_URL/opnfv-gerrit-$GERRIT_CHANGE_NUMBER.properties"
    # get the properties file for the Fuel ISO built for a merged change
    curl -s -o $WORKSPACE/latest.properties http://$GS_URL/opnfv-gerrit-$GERRIT_CHANGE_NUMBER.properties
else
    # get the latest.properties file in order to get info regarding latest artifact
    echo "Downloading http://$GS_URL/latest.properties"
    curl -s -o $WORKSPACE/latest.properties http://$GS_URL/latest.properties
fi

# check if we got the file
[[ -f latest.properties ]] || exit 1

# source the file so we get artifact metadata
source latest.properties

# echo the info about artifact that is used during the deployment
OPNFV_ARTIFACT=${OPNFV_ARTIFACT_URL/*\/}
echo "Using $OPNFV_ARTIFACT for deployment"

# check if we already have the ISO to avoid redownload
ISOSTORE_ROOT="/iso_mount/opnfv/${GIT_BRANCH##*/}"
if [[ -f "$ISOSTORE_ROOT/$OPNFV_ARTIFACT" ]]; then
    echo "ISO exists locally. Skipping the download and using the file from ISO store"
    /bin/cp -f $ISO_STORE/$OPNFV_ARTIFACT $WORKSPACE/opnfv.iso
    echo "--------------------------------------------------------"
    echo
    ls -al $WORKSPACE/opnfv.iso
    echo
    echo "--------------------------------------------------------"
    echo "Done!"
    exit 0
fi

# log info to console
echo "Downloading the $INSTALLER_TYPE artifact using URL http://$OPNFV_ARTIFACT_URL"
echo "This could take some time..."
echo "--------------------------------------------------------"
echo

# download the file
curl -s -o $WORKSPACE/opnfv.iso http://$OPNFV_ARTIFACT_URL > gsutil.iso.log 2>&1

# list the file
ls -al $WORKSPACE/opnfv.iso

echo
echo "--------------------------------------------------------"
echo "Done!"
