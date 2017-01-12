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

export TERM="vt220"

# source latest.properties if the ISO_VERSION is latest
if [[ "$ISO_VERSION" == "latest" ]]; then
    source latest.properties
    # echo the info about artifact that is used during the deployment
    echo "Using ${OPNFV_ARTIFACT_URL/*\/} for deployment"
else
    OPNFV_ARTIFACT_URL=$ISO_URL
    echo "Using $ISO_URL for deployment"
fi


if [[ "$JOB_NAME" =~ "merge" ]]; then
    # set simplest scenario for virtual deploys to run for merges
    DEPLOY_SCENARIO="os-nosdn-nofeature-ha"
else
    # for none-merge deployments
    # checkout theucommit that was used for building the downloaded artifact
    # to make sure the ISO and deployment mechanism uses same versions
    if [[ "$GIT_TAG" == "latest" ]]; then
        echo "Checking out $OPNFV_GIT_SHA1"
        git checkout $OPNFV_GIT_SHA1 --quiet
    else
        echo "Checking out $GIT_TAG"
        git checkout $GIT_TAG --quiet
    fi
fi

# set deployment parameters
export TMPDIR=$HOME/tmpdir
BRIDGE=${BRIDGE:-pxebr}
LAB_NAME=${NODE_NAME/-*}
POD_NAME=${NODE_NAME/*-}

if [[ "$NODE_NAME" =~ "virtual" ]]; then
    POD_NAME="virtual_kvm"
fi

# we currently support ericsson, intel, lf and zte labs
if [[ ! "$LAB_NAME" =~ (ericsson|intel|lf|zte) ]]; then
    echo "Unsupported/unidentified lab $LAB_NAME. Cannot continue!"
    exit 1
else
    echo "Using configuration for $LAB_NAME"
fi

# create TMPDIR if it doesn't exist
export TMPDIR=$HOME/tmpdir
mkdir -p $TMPDIR

# change permissions down to TMPDIR
chmod a+x $HOME
chmod a+x $TMPDIR

# clone the securedlab repo
# we should normally checkout colorado.3.0 for securedlab as well
# but ericsson-pod1 and ericsson-pod2 weren't there when colorado.3.0 was released
# so checking out that tag will probably cause issues. skipping the checkout.

cd $WORKSPACE
echo "Cloning securedlab repo ${GIT_BRANCH##origin/}"
git clone ssh://jenkins-ericsson@gerrit.opnfv.org:29418/securedlab --quiet \
    --branch ${GIT_BRANCH##origin/}
# log file name
FUEL_LOG_FILENAME="${JOB_NAME}_${BUILD_NUMBER}.log.tar.gz"

# construct the command
DEPLOY_COMMAND="sudo $WORKSPACE/ci/deploy.sh -b file://$WORKSPACE/securedlab \
    -l $LAB_NAME -p $POD_NAME -s $DEPLOY_SCENARIO -i file://$WORKSPACE/opnfv.iso \
    -H -B $BRIDGE -S $TMPDIR -L $WORKSPACE/$FUEL_LOG_FILENAME"

# log info to console
echo "Deployment parameters"
echo "--------------------------------------------------------"
echo "Scenario: $DEPLOY_SCENARIO"
echo "Lab: $LAB_NAME"
echo "POD: $POD_NAME"
echo "ISO: ${OPNFV_ARTIFACT_URL/*\/}"
echo
echo "Starting the deployment using $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

# start the deployment
echo "Issuing command"
echo "$DEPLOY_COMMAND"
echo

$DEPLOY_COMMAND
exit_code=$?

echo
echo "--------------------------------------------------------"
echo "Deployment is done!"

# upload logs for baremetal deployments
# work with virtual deployments is still going on so we skip that for the timebeing
if [[ "$JOB_NAME" =~ "baremetal-daily" ]]; then
    echo "Uploading deployment logs"
    gsutil cp $WORKSPACE/$FUEL_LOG_FILENAME gs://$GS_URL/logs/$FUEL_LOG_FILENAME > /dev/null 2>&1
    echo "Logs are available as http://$GS_URL/logs/$FUEL_LOG_FILENAME"
fi

if [[ $exit_code -ne 0 ]]; then
    echo "Deployment failed!"
    exit $exit_code
else
    echo "Deployment is successful!"
    exit 0
fi
