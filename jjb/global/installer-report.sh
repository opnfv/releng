#!/bin/bash
##############################################################################
# Copyright (c) 2017 ZTE Corporation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

eval $(cat /$WORKSPACE/installer_track.txt)
echo """
    INSTALLER: $INSTALLER
    JOB_NAME: $JOB_NAME
    BUILD_NUMBER: $BUILD_NUMBER
    PARENT_JOB_NAME: $PARENT_JOB_NAME:
    PARENT_BUILD_NUMBER: $PARENT_BUILD_NUMBER
    PROVISION_RESULT: $PROVISION_RESULT
    TIMESTAMP_START: $TIMESTAMP_START
    TIMESTAMP_END: `date '+%Y-%m-%d% %H:%M:%S'`
    NODE_NAME: $NODE_NAME
"""

echo "WIP: call testapi to report installer provisoin result"
