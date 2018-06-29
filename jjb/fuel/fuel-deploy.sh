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

if [[ "$BRANCH" =~ 'danube' ]]; then
    # source the file so we get OPNFV vars
    # shellcheck disable=SC1091
    source latest.properties

    # echo the info about artifact that is used during the deployment
    echo "Using ${OPNFV_ARTIFACT_URL/*\/} for deployment"

    # for Danube deployments (no artifact for current master or newer branches)
    # checkout the commit that was used for building the downloaded artifact
    # to make sure the ISO and deployment mechanism uses same versions
    echo "Checking out ${OPNFV_GIT_SHA1}"
    git checkout "${OPNFV_GIT_SHA1}" --quiet

    # releng wants us to use nothing else but opnfv.iso for now. We comply.
    ISO_FILE_ARG="-i file://${WORKSPACE}/opnfv.iso"
fi

# shellcheck disable=SC2153
if [[ "${JOB_NAME}" =~ 'verify' ]]; then
    # set simplest scenario for virtual deploys to run for verify
    DEPLOY_SCENARIO="os-nosdn-nofeature-noha"
fi

# set deployment parameters
export TMPDIR=${HOME}/tmpdir
# shellcheck disable=SC2153
LAB_NAME=${NODE_NAME/-*}
# shellcheck disable=SC2153
POD_NAME=${NODE_NAME/*-}
# Armband might override LAB_CONFIG_URL, all others use the default
LAB_CONFIG_URL=${LAB_CONFIG_URL:-'ssh://jenkins-ericsson@gerrit.opnfv.org:29418/securedlab'}

# Fuel requires deploy script to be ran with sudo, Armband does not
SUDO='sudo -E'
if [ "${PROJECT}" = 'fuel' ]; then
    # Fuel currently supports ericsson, intel, lf and zte labs
    if [[ ! "${LAB_NAME}" =~ (ericsson|intel|lf|zte) ]]; then
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
chmod a+x "${HOME}" "${TMPDIR}"

cd "${WORKSPACE}" || exit 1
if [[ "$BRANCH" =~ (danube|euphrates) ]]; then
    if [[ "${LAB_CONFIG_URL}" =~ ^(git|ssh):// ]]; then
        echo "Cloning securedlab repo ${BRANCH}"
        LOCAL_CFG="${TMPDIR}/securedlab"
        rm -rf "${LOCAL_CFG}"
        git clone --quiet --branch "${BRANCH}" "${LAB_CONFIG_URL}" "${LOCAL_CFG}"
        LAB_CONFIG_ARG="-b file://${LOCAL_CFG}"
        BRIDGE_ARG="-B ${BRIDGE:-pxebr}"
    else
        LAB_CONFIG_ARG="-b ${LAB_CONFIG_URL}"
    fi
fi

# log file name
FUEL_LOG_FILENAME="${JOB_NAME}_${BUILD_NUMBER}.log.tar.gz"

# construct the command
DEPLOY_COMMAND="${SUDO} ${WORKSPACE}/ci/deploy.sh ${LAB_CONFIG_ARG:-} \
    -l ${LAB_NAME} -p ${POD_NAME} -s ${DEPLOY_SCENARIO} ${ISO_FILE_ARG:-} \
    -S ${TMPDIR} ${BRIDGE_ARG:-} \
    -L ${WORKSPACE}/${FUEL_LOG_FILENAME}"

# log info to console
echo "Deployment parameters"
echo "--------------------------------------------------------"
echo "Scenario: ${DEPLOY_SCENARIO}"
echo "Lab: ${LAB_NAME}"
echo "POD: ${POD_NAME}"
[[ "${BRANCH}" =~ 'danube' ]] && echo "ISO: ${OPNFV_ARTIFACT_URL/*\/}"
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

# Temporary workaround for ericsson-virtual* PODs functest integration
# See https://jira.opnfv.org/browse/FUNCTEST-985
# Set iptables rule to allow forwarding return traffic for container
redirect=/dev/stdout
if ! sudo iptables -C FORWARD -j RETURN 2> ${redirect} || \
   ! sudo iptables -L FORWARD | awk 'NR==3' | grep RETURN 2> ${redirect}; then
     sudo iptables -I FORWARD -j RETURN
fi

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
