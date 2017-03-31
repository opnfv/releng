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

cd $WORKSPACE/prototypes/xci

# for daily jobs, we want to use working versions
# for periodic jobs, we will use whatever is set in the job, probably master
if [[ "$JOB_NAME" =~ "daily" ]]; then
    # source pinned-vars to get releng version
    source ./config/pinned-versions

    # checkout the version
    git checkout -q $OPNFV_RELENG_VERSION
    echo "Info: Using $OPNFV_RELENG_VERSION"
elif [[ "$JOB_NAME" =~ "periodic" ]]; then
    echo "Info: Using $OPNFV_RELENG_VERSION"
fi

# proceed with the deployment
cd $WORKSPACE/prototypes/xci
sudo -E ./xci-deploy.sh
