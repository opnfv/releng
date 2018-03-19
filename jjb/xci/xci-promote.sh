#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 Ericsson and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

#----------------------------------------------------------------------
# This script is used by CI and executed by Jenkins jobs.
# You are not supposed to use this script manually if you don't know
# what you are doing.
#----------------------------------------------------------------------

# ensure GERRIT_TOPIC is set
GERRIT_TOPIC="${GERRIT_TOPIC:-''}"

# skip the healthcheck if the patch doesn't impact the deployment
if [[ "$GERRIT_TOPIC" =~ skip-verify|skip-deployment ]]; then
    echo "Skipping the healthcheck!"
    exit 0
fi

# fail if promotion metadata file doesn't exist
if [ ! -f $LOCAL_PROMOTION_METADATA_FILE ]; then
    echo "Unable to find promotion metadata file $LOCAL_PROMOTION_METADATA_FILE"
    echo "Skipping promotion!"
    exit 1
fi

# upload promotion metadata file to OPNFV artifact repo
echo "Storing promotion metadata as $REMOTE_PROMOTION_METADATA_FILE"
gsutil cp $LOCAL_PROMOTION_METADATA_FILE $REMOTE_PROMOTION_METADATA_FILE > /dev/null 2>&1

# update the file metadata on gs to prevent the use of cached version of the file
gsutil -m setmeta -r -h "Cache-Control:private, max-age=0, no-transform" \
    $REMOTE_PROMOTION_METADATA_FILE > /dev/null 2>&1

# log the metadata to console
echo "Stored the metadata for $DEPLOY_SCENARIO"
echo "---------------------------------------------------------------------------------"
gsutil cat $REMOTE_PROMOTION_METADATA_FILE
echo "---------------------------------------------------------------------------------"
echo "Scenario $DEPLOY_SCENARIO has successfully been promoted!"
