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

if [[ "$GERRIT_CHANGE_NUMBER" == "none" || "$GERRIT_PATCHSET_NUMBER" == "none" ]]; then
    echo "You need to provide GERRIT_CHANGE_NUMBER and/or GERRIT_PATCHSET_NUMBER"
    exit 1
fi

OPNFV_ARTIFACT_URL="http://artifacts.opnfv.org/fuel/gerrit-${GERRIT_CHANGE_NUMBER}.iso"
# echo the info about artifact that is used during the deployment
echo "Using ${OPNFV_ARTIFACT_URL/*\/} for deployment"

# try to download the artifact
wget -O $WORKSPACE/opnfv.iso $OPNFV_ARTIFACT_URL
if [[ $? -ne 0 ]]; then
    echo "Unable to download the artifact using URL  $OPNFV_ARTIFACT_URL"
    exit 1
fi

# set deployment parameters
export TMPDIR=$HOME/tmpdir
BRIDGE=pxebr
LAB_NAME=${NODE_NAME/-*}
POD_NAME=${NODE_NAME/*-}

if [[ "$NODE_NAME" == "opnfv-jump-2" ]]; then
    LAB_NAME="lf"
    POD_NAME="pod2"
fi

if [[ "$NODE_NAME" =~ "virtual" ]]; then
    POD_NAME="virtual_kvm"
fi

# we currently support ericsson, intel, and lf labs
if [[ ! "$LAB_NAME" =~ (ericsson|intel|lf) ]]; then
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

# get the last 2 digits of the change number
GERRIT_CHANGE_SHORT_NUMBER=${GERRIT_CHANGE_NUMBER:(-2)}

# change ref
CHANGE_REF="refs/changes/$GERRIT_CHANGE_SHORT_NUMBER/$GERRIT_CHANGE_NUMBER/$GERRIT_PATCHSET_NUMBER"
echo "Checking out $CHANGE_REF"

# checkout the patch
cd $WORKSPACE
git fetch https://gerrit.opnfv.org/gerrit/fuel $CHANGE_REF && git checkout FETCH_HEAD
if [[ $? -ne 0 ]]; then
    echo "Unable to checkout $CHANGE_REF"
    exit 1
fi

# clone the securedlab repo
echo "Cloning securedlab repo ${GIT_BRANCH##origin/}"
git clone ssh://jenkins-ericsson@gerrit.opnfv.org:29418/securedlab \
    --quiet --branch $GIT_BRANCH

# construct the command
DEPLOY_COMMAND="sudo $WORKSPACE/ci/deploy.sh -b file://$WORKSPACE/securedlab -l $LAB_NAME -p $POD_NAME -s $DEPLOY_SCENARIO -i file://$WORKSPACE/opnfv.iso -H -B $BRIDGE -S $TMPDIR"

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
