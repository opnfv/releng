#!/bin/bash
##############################################################################
# Copyright (c) 2016 ZTE Coreporation and others.
# hu.zhijiang@zte.com.cn
# sun.jing22@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o pipefail

# use proxy url to replace the nomral URL, for googleusercontent.com will be blocked randomly
[[ "$NODE_NAME" =~ (zte) ]] && GS_URL=${GS_BASE_PROXY%%/*}/$GS_URL

if [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Downloading http://$GS_URL/opnfv-gerrit-$GERRIT_CHANGE_NUMBER.properties"
    # get the properties file for the Daisy4nfv BIN built for a merged change
    curl -L -s -o $WORKSPACE/latest.properties http://$GS_URL/opnfv-gerrit-$GERRIT_CHANGE_NUMBER.properties
else
    # get the latest.properties file in order to get info regarding latest artifact
    echo "Downloading http://$GS_URL/latest.properties"
    curl -L -s -o $WORKSPACE/latest.properties http://$GS_URL/latest.properties
fi

# check if we got the file
[[ -f $WORKSPACE/latest.properties ]] || exit 1

# source the file so we get artifact metadata
source $WORKSPACE/latest.properties

# echo the info about artifact that is used during the deployment
OPNFV_ARTIFACT=${OPNFV_ARTIFACT_URL/*\/}
echo "Using $OPNFV_ARTIFACT for deployment"

[[ "$NODE_NAME" =~ (zte) ]] && OPNFV_ARTIFACT_URL=${GS_BASE_PROXY%%/*}/$OPNFV_ARTIFACT_URL

if [[ ! "$JOB_NAME" =~ (verify|merge) ]]; then
    # check if we already have the image to avoid redownload
    BINSTORE="/bin_mount/opnfv_ci/${BRANCH##*/}"
    if [[ -f "$BINSTORE/$OPNFV_ARTIFACT" && ! -z $OPNFV_ARTIFACT_SHA512SUM ]]; then
        echo "BIN exists locally. Starting to check the sha512sum."
        if [[ $OPNFV_ARTIFACT_SHA512SUM = $(sha512sum -b $BINSTORE/$OPNFV_ARTIFACT | cut -d' ' -f1) ]]; then
            echo "Sha512sum is verified. Skipping the download and using the file from BIN store."
            ln -s $BINSTORE/$OPNFV_ARTIFACT $WORKSPACE/opnfv.bin
            echo "--------------------------------------------------------"
            echo
            ls -al $WORKSPACE/opnfv.bin
            echo
            echo "--------------------------------------------------------"
            echo "Done!"
            exit 0
        fi
    fi
fi

# log info to console
echo "Downloading the $INSTALLER_TYPE artifact using URL http://$OPNFV_ARTIFACT_URL"
echo "This could take some time... Now the time is $(date -u)"
echo "--------------------------------------------------------"
echo

# download the file
if [[ "$NODE_NAME" =~ (zte) ]] && [ `command -v aria2c` ]; then
    aria2c -x 3 -o $WORKSPACE/opnfv.bin http://$OPNFV_ARTIFACT_URL > gsutil.bin.log 2>&1
else
    curl -L -s -o $WORKSPACE/opnfv.bin http://$OPNFV_ARTIFACT_URL > gsutil.bin.log 2>&1
fi

# list the file
ls -al $WORKSPACE/opnfv.bin

echo
echo "--------------------------------------------------------"
echo "Done!"
