#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
#           (c) 2017 Enea Software AB
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o nounset
set -o pipefail

export TERM="vt220"

if [[ "$BRANCH" != 'master' ]]; then
    # source the file so we get OPNFV vars
    source latest.properties

    # echo the info about artifact that is used during the deployment
    echo "Using ${OPNFV_ARTIFACT_URL/*\/} for deployment"
fi

if [[ "$JOB_NAME" =~ "merge" ]]; then
    # set simplest scenario for virtual deploys to run for merges
    DEPLOY_SCENARIO="os-nosdn-nofeature-ha"
elif [[ "$BRANCH" != 'master' ]]; then
    # for none-merge deployments
    # checkout the commit that was used for building the downloaded artifact
    # to make sure the ISO and deployment mechanism uses same versions
    echo "Checking out $OPNFV_GIT_SHA1"
    git checkout $OPNFV_GIT_SHA1 --quiet
fi

# set deployment parameters
export TMPDIR=${WORKSPACE}/tmpdir

# arm-pod4 is an aarch64 jenkins slave for the same POD as the
# x86 jenkins slave arm-pod3; therefore we use the same pod name
# to deploy the pod from both jenkins slaves
if [[ "${NODE_NAME}" == "arm-pod4" ]]; then
    NODE_NAME="arm-pod3"
fi

LAB_NAME=${NODE_NAME/-*}
POD_NAME=${NODE_NAME/*-}

# we currently support enea
if [[ ! $LAB_NAME =~ (arm|enea) ]]; then
    echo "Unsupported/unidentified lab $LAB_NAME. Cannot continue!"
    exit 1
fi

echo "Using configuration for $LAB_NAME"

# create TMPDIR if it doesn't exist
mkdir -p $TMPDIR

cd $WORKSPACE
if [[ $LAB_CONFIG_URL =~ ^(git|ssh):// ]]; then
    echo "Cloning securedlab repo $BRANCH"
    git clone --quiet --branch $BRANCH $LAB_CONFIG_URL lab-config
    LAB_CONFIG_URL=file://${WORKSPACE}/lab-config

    # Source local_env if present, which contains POD-specific config
    local_env="${WORKSPACE}/lab-config/labs/$LAB_NAME/$POD_NAME/fuel/config/local_env"
    if [ -e $local_env ]; then
        echo "-- Sourcing local environment file"
        source $local_env
    fi
fi

if [[ "$NODE_NAME" =~ "virtual" ]]; then
    POD_NAME="virtual_kvm"
fi

# releng wants us to use nothing else but opnfv.iso for now. We comply.
ISO_FILE=$WORKSPACE/opnfv.iso

# log file name
FUEL_LOG_FILENAME="${JOB_NAME}_${BUILD_NUMBER}.log.tar.gz"

# Deploy Cache (to enable just create the deploy-cache subdir)
# NOTE: Only available when ISO files are cached using ISOSTORE mechanism
DEPLOY_CACHE=${ISOSTORE:-/iso_mount/opnfv_ci}/${BRANCH##*/}/deploy-cache
if [[ -d "${DEPLOY_CACHE}" ]]; then
    echo "Deploy cache dir present."
    echo "--------------------------------------------------------"
    echo "Fuel@OPNFV deploy cache: ${DEPLOY_CACHE}"
    DEPLOY_CACHE="-C ${DEPLOY_CACHE}"
else
    DEPLOY_CACHE=""
fi

# construct the command
DEPLOY_COMMAND="sudo -E $WORKSPACE/ci/deploy.sh -b ${LAB_CONFIG_URL} \
    -l $LAB_NAME -p $POD_NAME -s $DEPLOY_SCENARIO -i file://${ISO_FILE} \
    -H -B ${DEFAULT_BRIDGE:-pxebr} -S $TMPDIR -L $WORKSPACE/$FUEL_LOG_FILENAME \
    ${DEPLOY_CACHE}"

# log info to console
echo "Deployment parameters"
echo "--------------------------------------------------------"
echo "Scenario: $DEPLOY_SCENARIO"
echo "Lab: $LAB_NAME"
echo "POD: $POD_NAME"
[[ "$BRANCH" != 'master' ]] && echo "ISO: ${OPNFV_ARTIFACT_URL/*\/}"
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
fi
