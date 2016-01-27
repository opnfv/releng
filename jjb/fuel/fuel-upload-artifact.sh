#!/bin/bash
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# fatih.degirmenci@ericsson.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

# check if we built something
if [ -f $WORKSPACE/.noupload ]; then
    echo "Nothing new to upload. Exiting."
    /bin/rm -f $WORKSPACE/.noupload
    exit 0
fi

# log info to console
echo
echo "Uploading the $INSTALLER_TYPE artifact. This could take some time..."
echo

# source the opnfv.properties to get ARTIFACT_VERSION
source $WORKSPACE/opnfv.properties

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
    gs://$GS_URL/*.properties > /dev/null 2>&1

gsutil -m setmeta \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/*.iso > /dev/null 2>&1

echo "Done!"
echo
echo "--------------------------------------------------------"
echo
echo "Artifact is available as http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
echo
echo "--------------------------------------------------------"
echo
