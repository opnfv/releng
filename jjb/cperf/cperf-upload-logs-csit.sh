#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

LOGS_LOCATION=/tmp/robot_results
UPLOAD_LOCATION=artifacts.opnfv.org/cperf/cperf-apex-csit-${ODL_BRANCH}/${BUILD_NUMBER}/
echo "Uploading robot logs to ${UPLOAD_LOCATION}"
gsutil -m cp -r -v ${LOGS_LOCATION} gs://${UPLOAD_LOCATION} > gsutil.latest_logs.log
