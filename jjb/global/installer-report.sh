#!/bin/bash

eval $(cat /tmp/installer_track.txt)
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
