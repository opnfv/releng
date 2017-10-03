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

# Fuel requires deploy script to be ran with sudo, Armband does not
SUDO='sudo -E'
[ "${PROJECT}" = 'fuel' ] || SUDO=

# Log file name
FUEL_PM_LOG_FILENAME="${JOB_NAME}_${BUILD_NUMBER}_pm.log.tar.gz"

# Construct the command
LOG_COMMAND="${SUDO} ${WORKSPACE}/mcp/scripts/log.sh \
             ${WORKSPACE}/${FUEL_PM_LOG_FILENAME}"

# Log info to console
echo "Collecting post mortem logs ..."
echo "--------------------------------------------------------"
echo "${LOG_COMMAND}"

${LOG_COMMAND}

# Upload logs for both baremetal and virtual deployments
echo "Uploading deployment logs"
echo "--------------------------------------------------------"
gsutil cp "${WORKSPACE}/${FUEL_PM_LOG_FILENAME}" \
    "gs://${GS_URL}/logs/${FUEL_PM_LOG_FILENAME}" > /dev/null 2>&1
echo "Logs are available at http://${GS_URL}/logs/${FUEL_PM_LOG_FILENAME}"
