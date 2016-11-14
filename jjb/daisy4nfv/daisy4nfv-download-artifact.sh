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

if [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Downloading http://$GS_URL/opnfv-gerrit-$GERRIT_CHANGE_NUMBER.properties"
    # get the properties file for the Daisy4nfv BIN built for a merged change
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

# log info to console
echo "Downloading the $INSTALLER_TYPE artifact using URL http://$OPNFV_ARTIFACT_URL"
echo "This could take some time..."
echo "--------------------------------------------------------"
echo

# download the file
curl -s -o $WORKSPACE/opnfv.bin http://$OPNFV_ARTIFACT_URL > gsutil.bin.log 2>&1

# list the file
ls -al $WORKSPACE/opnfv.bin

echo
echo "--------------------------------------------------------"
echo "Done!"
