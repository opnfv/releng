#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o nounset
set -o pipefail

# check if we built something
if [ -f $WORKSPACE/.noupload ]; then
    echo "Nothing new to upload. Exiting."
    /bin/rm -f $WORKSPACE/.noupload
    exit 0
fi

# source the opnfv.properties to get ARTIFACT_VERSION
source $WORKSPACE/opnfv.properties

# store ISO locally on NFS first
ISOSTORE_ROOT="/iso_mount/opnfv/${GIT_BRANCH##*/}"
if [[ -d $ISOSTORE_ROOT ]]; then
    # storing ISOs for verify & merge jobs will be done once we get the disk array
    if [[ ! "$JOB_NAME" =~ (verify|merge) ]]; then
        # remove all but most recent 5 ISOs first to keep iso_mount clean & tidy
        cd $ISOSTORE_ROOT
        ls -tp | grep -v '/' | tail -n +6 | xargs -d '\n' /bin/rm -f --

        # store ISO
        echo "Storing $INSTALLER_TYPE artifact on NFS first"
        /bin/cp -f $BUILD_DIRECTORY/opnfv-$OPNFV_ARTIFACT_VERSION.iso \
            $ISOSTORE_ROOT/$branch/opnfv-$OPNFV_ARTIFACT_VERSION.iso
    fi
fi

# log info to console
echo
echo "Uploading $INSTALLER_TYPE artifact. This could take some time..."
echo

# upload artifact and additional files to google storage
gsutil cp $BUILD_DIRECTORY/opnfv-$OPNFV_ARTIFACT_VERSION.iso \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso > gsutil.iso.log 2>&1
gsutil cp $WORKSPACE/opnfv.properties \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log 2>&1
if [[ ! "$JOB_NAME" =~ (verify|merge) ]]; then
    gsutil cp $WORKSPACE/opnfv.properties \
    gs://$GS_URL/latest.properties > gsutil.latest.log 2>&1
elif [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Uploaded Fuel ISO for a merged change"
fi

gsutil -m setmeta \
    -h "Content-Type:text/html" \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/latest.properties \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > /dev/null 2>&1

gsutil -m setmeta \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso > /dev/null 2>&1

# disabled errexit due to gsutil setmeta complaints
#   BadRequestException: 400 Invalid argument
# check if we uploaded the file successfully to see if things are fine
gsutil ls gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Problem while uploading artifact!"
    echo "Check log $WORKSPACE/gsutil.iso.log on the machine where this build is done."
    exit 1
fi

echo "Done!"
echo
echo "--------------------------------------------------------"
echo
echo "Artifact is available as http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
echo
echo "--------------------------------------------------------"
echo
