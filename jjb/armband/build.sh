#!/bin/bash
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

cd $WORKSPACE

# get current SHA1
CURRENT_SHA1=$(git rev-parse HEAD)

# log info to console
echo "Starting the build of Armband. This could take some time..."
echo "-----------------------------------------------------------"
echo

# set OPNFV_ARTIFACT_VERSION
if [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Building Fuel ISO for a merged change"
    export OPNFV_ARTIFACT_VERSION="gerrit-$GERRIT_CHANGE_NUMBER"
    echo "Not supported"
    exit 1
else
    export OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
fi

NOCACHE_PATTERN="verify: no-cache"
if [[ "$JOB_NAME" =~ "verify" && "$GERRIT_CHANGE_COMMIT_MESSAGE" =~ "$NOCACHE_PATTERN" ]]; then
    echo "The cache will not be used for this build!"
    NOCACHE_ARG="-f P"
fi
NOCACHE_ARG=${NOCACHE_ARG:-}

# start the build
cd $WORKSPACE/ci
./build.sh $BUILD_DIRECTORY

# list the build artifacts
ls -al $BUILD_DIRECTORY

# save information regarding artifact into file
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
    echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
    echo "OPNFV_ARTIFACT_URL=$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
) > $WORKSPACE/opnfv.properties

echo
echo "--------------------------------------------------------"
echo "Done!"
