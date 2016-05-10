#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
#           (c) 2016 Enea Software AB
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

# source the file so we get OPNFV vars
source latest.properties

# echo the info about artifact that is used during the deployment
echo "Using ${OPNFV_ARTIFACT_URL/*\/} for deployment"

if [[ "$JOB_NAME" =~ "merge" ]]; then
    # set simplest scenario for virtual deploys to run for merges
    DEPLOY_SCENARIO="os-nosdn-nofeature-ha"
else
    # for none-merge deployments
    # checkout the commit that was used for building the downloaded artifact
    # to make sure the ISO and deployment mechanism uses same versions
    echo "Checking out $OPNFV_GIT_SHA1"
    git checkout $OPNFV_GIT_SHA1 --quiet
fi

# set deployment parameters
export TMPDIR=$HOME/tmpdir
BRIDGE=${DEFAULT_BRIDGE:-pxebr}
LAB_NAME=${NODE_NAME/-*}
POD_NAME=${NODE_NAME/*-}

# we currently support enea
if [[ ! "$LAB_NAME" =~ "enea" ]]; then
    echo "Unsupported/unidentified lab $LAB_NAME. Cannot continue!"
    exit 1
else
    echo "Using configuration for $LAB_NAME"
fi

# create TMPDIR if it doesn't exist
mkdir -p $TMPDIR

cd $WORKSPACE
if [[ $LAB_CONFIG_URL =~ ^git:// ]]; then
    git clone --quiet --branch ${GIT_BRANCH##origin/} $LAB_CONFIG_URL lab-config
    LAB_CONFIG_URL=file://${WORKSPACE}/lab-config
fi

# construct the command
DEPLOY_COMMAND="$WORKSPACE/ci/deploy.sh -b ${LAB_CONFIG_URL} -l $LAB_NAME -p $POD_NAME -s $DEPLOY_SCENARIO -i file://$WORKSPACE/opnfv.iso -H -B $BRIDGE -S $TMPDIR"

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

echo
echo "--------------------------------------------------------"
echo "Deployment is done successfully!"
