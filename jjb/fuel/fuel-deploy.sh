#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 Ericsson AB, Mirantis Inc., Enea Software AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o nounset
set -o pipefail

export TERM="vt220"

# set deployment parameters
export TMPDIR=${HOME}/tmpdir
# shellcheck disable=SC2153
LAB_NAME=${NODE_NAME/-*}
# shellcheck disable=SC2153
POD_NAME=${NODE_NAME/*-}

# Fuel requires deploy script to be ran with sudo, Armband does not
SUDO='sudo -E'
if [ "${PROJECT}" = 'fuel' ]; then
    # Fuel currently supports ericsson, intel, lf and zte labs
    if [[ ! "${LAB_NAME}" =~ (arm|enea|ericsson|intel|lf|unh|zte) ]]; then
        echo "Unsupported/unidentified lab ${LAB_NAME}. Cannot continue!"
        exit 1
    fi
else
    SUDO=
    # Armband currently supports arm, enea, unh labs
    if [[ ! "${LAB_NAME}" =~ (arm|enea|unh) ]]; then
        echo "Unsupported/unidentified lab ${LAB_NAME}. Cannot continue!"
        exit 1
    fi
fi

echo "Using configuration for ${LAB_NAME}"

# create TMPDIR if it doesn't exist, change permissions
mkdir -p "${TMPDIR}"
sudo chmod a+x "${HOME}" "${TMPDIR}"

cd "${WORKSPACE}" || exit 1

# log file name
FUEL_LOG_FILENAME="${JOB_NAME}_${BUILD_NUMBER}.log.tar.gz"

# Limited scope for vPOD verify jobs running on armband-virtual
[[ ! "${JOB_NAME}" =~ verify-deploy-virtual-arm64 ]] || EXTRA_ARGS='-e'

# construct the command
DEPLOY_COMMAND="${SUDO} ${WORKSPACE}/ci/deploy.sh \
    -l ${LAB_NAME} -p ${POD_NAME} -s ${DEPLOY_SCENARIO} \
    -S ${TMPDIR} ${EXTRA_ARGS:-} \
    -L ${WORKSPACE}/${FUEL_LOG_FILENAME}"

# log info to console
echo "Deployment parameters"
echo "--------------------------------------------------------"
echo "Scenario: ${DEPLOY_SCENARIO}"
echo "Lab: ${LAB_NAME}"
echo "POD: ${POD_NAME}"
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
if [[ "${JOB_NAME}" =~ baremetal-daily ]]; then
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
