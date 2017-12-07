#!/bin/bash
##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

source $WORKSPACE/installer_track.sh
echo """
    INSTALLER: $INSTALLER
    INSTALLER_VERSION: $INSTALLER_VERSION
    JOB_NAME: $JOB_NAME
    BUILD_ID: $BUILD_ID
    SENARIO: $DEPLOY_SCENARIO
    UPSTREAM_JOB_NAME: $UPSTREAM_JOB_NAME:
    UPSTREAM_BUILD_ID: $UPSTREAM_BUILD_ID
    PROVISION_RESULT: $PROVISION_RESULT
    TIMESTAMP_START: $TIMESTAMP_START
    TIMESTAMP_END: `date '+%Y-%m-%d %H:%M:%S.%3N'`
    POD_NAME: $NODE_NAME
"""

# TODO call TestAPI to report installer provisoin result when API is ready
