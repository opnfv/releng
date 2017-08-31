#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2017 Ericsson AB, Mirantis Inc., Enea Software AB and others.
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

# shellcheck disable=SC2153
if [[ "${JOB_NAME}" =~ "merge" ]]; then
    # set simplest scenario for virtual deploys to run for merges
    DEPLOY_SCENARIO="os-nosdn-nofeature-ha"
elif [[ "${BRANCH}" != 'master' ]]; then
    # for none-merge deployments
    # checkout the commit that was used for building the downloaded artifact
    # to make sure the ISO and deployment mechanism uses same versions
    echo "Checking out ${OPNFV_GIT_SHA1}"
    git checkout "${OPNFV_GIT_SHA1}" --quiet
fi

# set deployment parameters
export TMPDIR=${HOME}/tmpdir
BRIDGE=${BRIDGE:-pxebr}
# shellcheck disable=SC2153
LAB_NAME=${NODE_NAME/-*}
# shellcheck disable=SC2153
POD_NAME=${NODE_NAME/*-}
# Fuel requires deploy script to be ran with sudo
SUDO=sudo

if [[ "${NODE_NAME}" =~ "virtual" ]]; then
    POD_NAME="virtual_kvm"
fi

# we currently support ericsson, intel, lf and zte labs
if [[ ! "${LAB_NAME}" =~ (ericsson|intel|lf|zte) ]]; then
    echo "Unsupported/unidentified lab ${LAB_NAME}. Cannot continue!"
    exit 1
fi

echo "Using configuration for ${LAB_NAME}"

# create TMPDIR if it doesn't exist, change permissions
mkdir -p "${TMPDIR}"
chmod a+x "${HOME}" "${TMPDIR}"

# TODO: move lab-config URL to Jenkins param
LAB_CONFIG_URL='ssh://jenkins-ericsson@gerrit.opnfv.org:29418/securedlab'

cd "${WORKSPACE}" || exit 1
if [[ "${LAB_CONFIG_URL}" =~ ^(git|ssh):// ]]; then
    echo "Cloning securedlab repo ${BRANCH}"
    git clone --quiet --branch "${BRANCH}" "${LAB_CONFIG_URL}" lab-config
    LAB_CONFIG_URL=file://${WORKSPACE}/lab-config

    # Source local_env if present, which contains POD-specific config
    local_env="${WORKSPACE}/lab-config/labs/${LAB_NAME}/${POD_NAME}/fuel/config/local_env"
    if [ -e "${local_env}" ]; then
        echo "-- Sourcing local environment file"
        source "${local_env}"
    fi
fi

# releng wants us to use nothing else but opnfv.iso for now. We comply.
ISO_FILE=file://${WORKSPACE}/opnfv.iso

# log file name
FUEL_LOG_FILENAME="${JOB_NAME}_${BUILD_NUMBER}.log.tar.gz"

# construct the command
DEPLOY_COMMAND="${SUDO} ${WORKSPACE}/ci/deploy.sh -b ${LAB_CONFIG_URL} \
    -l ${LAB_NAME} -p ${POD_NAME} -s ${DEPLOY_SCENARIO} -i ${ISO_FILE} \
    -B ${DEFAULT_BRIDGE:-${BRIDGE}} -S ${TMPDIR} \
    -L ${WORKSPACE}/${FUEL_LOG_FILENAME}"

# log info to console
echo "Deployment parameters"
echo "--------------------------------------------------------"
echo "Scenario: ${DEPLOY_SCENARIO}"
echo "Lab: ${LAB_NAME}"
echo "POD: ${POD_NAME}"
[[ "${BRANCH}" != 'master' ]] && echo "ISO: ${OPNFV_ARTIFACT_URL/*\/}"
echo
echo "Starting the deployment using ${INSTALLER_TYPE}. This could take some time..."
echo "--------------------------------------------------------"
echo

# start the deployment
echo "Issuing command"
echo "${DEPLOY_COMMAND}"
echo

${DEPLOY_COMMAND}
exit_code=$?

echo
echo "--------------------------------------------------------"
echo "Deployment is done!"

# upload logs for baremetal deployments
# work with virtual deployments is still going on, so skip that for now
if [[ "${JOB_NAME}" =~ (baremetal-daily|baremetal-weekly) ]]; then
    echo "Uploading deployment logs"
    gsutil cp "${WORKSPACE}/${FUEL_LOG_FILENAME}" \
        "gs://${GS_URL}/logs/${FUEL_LOG_FILENAME}" > /dev/null 2>&1
    echo "Logs are available at http://${GS_URL}/logs/${FUEL_LOG_FILENAME}"
fi

if [[ "${exit_code}" -ne 0 ]]; then
    echo "Deployment failed!"
    exit "${exit_code}"
fi

echo "Deployment is successful!"
exit 0
