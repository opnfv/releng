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

# do not continue with the deployment if FRESH_INSTALL is not requested
if [[ "$FRESH_INSTALL" == "true" ]]; then
    echo "Fresh install requested. Proceeding with the installation."
else
    echo "Fresh install is not requested. Skipping the installation."
    exit 0
fi

export TERM="vt220"

# get the latest successful job console log and extract the properties filename
FUEL_DEPLOY_BUILD_URL="https://build.opnfv.org/ci/job/fuel-deploy-virtual-daily-master/lastSuccessfulBuild/consoleText"
FUEL_PROPERTIES_FILE=$(curl -s -L ${FUEL_DEPLOY_URL} | grep 'ISO:' | awk '{print $2}' | sed 's/iso/properties/g')
if [[ -z "FUEL_PROPERTIES_FILE" ]]; then
    echo "Unable to extract the url to Fuel ISO properties from ${FUEL_DEPLOY_URL}"
    exit 1
fi
curl -L -s -o $WORKSPACE/latest.properties http://artifacts.opnfv.org/fuel/$FUEL_PROPERTIES_FILE

# source the file so we get OPNFV vars
source latest.properties

# echo the info about artifact that is used during the deployment
echo "Using ${OPNFV_ARTIFACT_URL/*\/} for deployment"

# download the iso
echo "Downloading the ISO using the link http://$OPNFV_ARTIFACT_URL"
curl -L -s -o $WORKSPACE/opnfv.iso http://$OPNFV_ARTIFACT_URL > gsutil.iso.log 2>&1

echo "Checking out $OPNFV_GIT_SHA1"
git checkout $OPNFV_GIT_SHA1 --quiet

# set deployment parameters
DEPLOY_SCENARIO="os-nosdn-nofeature-noha"
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

if [[ $exit_code -ne 0 ]]; then
    echo "Deployment failed!"
    exit $exit_code
else
    echo "Deployment is successful!"
    exit 0
fi
