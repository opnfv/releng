#!/bin/bash
##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

source $WORKSPACE/installer_track.sh

gen_content()
{
    cat <<EOF
{
    "installer": "$INSTALLER",
    "version": "$INSTALLER_VERSION",
    "pod_name": "$POD_NAME",
    "job_name": "$JOB_NAME",
    "build_id": "$BUILD_ID",
    "scenario": "$SCENARIO",
    "upstream_job_name": "$UPSTREAM_JOB_NAME",
    "upstream_build_id":"$UPSTREAM_BUILD_ID",
    "criteria": "$PROVISION_RESULT",
    "start_date": "$TIMESTAMP_START",
    "stop_date": "$TIMESTAMP_END",
    "detail":""
}
EOF
}

echo "Installer: $INSTALLER provision result: $PROVISION_RESULT"
echo $(gen_content)

set -o xtrace
TESTAPI_URL=http://testresults.opnfv.org/test/api/v1/deployresults
curl -H "Content-Type: application/json" -X POST -v -d "$(gen_content)" $TESTAPI_URL
