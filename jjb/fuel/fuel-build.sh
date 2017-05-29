#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# disable Fuel iso build for master branch
[ "$BRANCH" = 'master' ] && exit 0

set -o errexit
set -o nounset
set -o pipefail

export TERM="vt220"

cd $WORKSPACE

# remove the expired items from cache
test -f $WORKSPACE/ci/clean_cache.sh && $WORKSPACE/ci/clean_cache.sh $CACHE_DIRECTORY

LATEST_ISO_PROPERTIES=$WORKSPACE/latest.iso.properties
if [[ "$JOB_NAME" =~ "daily" ]]; then
    # check to see if we already have an artifact on artifacts.opnfv.org
    # for this commit during daily builds
    echo "Checking to see if we already built and stored Fuel ISO for this commit"

    curl -s -o $LATEST_ISO_PROPERTIES http://$GS_URL/latest.properties 2>/dev/null
fi

# get metadata of latest ISO
if grep -q OPNFV_GIT_SHA1 $LATEST_ISO_PROPERTIES 2>/dev/null; then
    LATEST_ISO_SHA1=$(grep OPNFV_GIT_SHA1 $LATEST_ISO_PROPERTIES | cut -d'=' -f2)
    LATEST_ISO_URL=$(grep OPNFV_ARTIFACT_URL $LATEST_ISO_PROPERTIES | cut -d'=' -f2)
else
    LATEST_ISO_SHA1=none
fi

# get current SHA1
CURRENT_SHA1=$(git rev-parse HEAD)

# set FORCE_BUILD to false for non-daily builds
FORCE_BUILD=${FORCE_BUILD:-false}

if [[ "$CURRENT_SHA1" == "$LATEST_ISO_SHA1" && "$FORCE_BUILD" == "false" ]]; then
    echo "***************************************************"
    echo "   An ISO has already been built for this commit"
    echo "   $LATEST_ISO_URL"
    echo "***************************************************"
#    echo "Nothing new to build. Exiting."
#    touch $WORKSPACE/.noupload
#    exit 0
else
    echo "This commit has not been built yet or forced build! Proceeding with the build."
    /bin/rm -f $LATEST_ISO_PROPERTIES
    echo
fi

# log info to console
echo "Starting the build of $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

# create the cache directory if it doesn't exist
mkdir -p $CACHE_DIRECTORY

# set OPNFV_ARTIFACT_VERSION
if [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Building Fuel ISO for a merged change"
    export OPNFV_ARTIFACT_VERSION="gerrit-$GERRIT_CHANGE_NUMBER"
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
./build.sh -v $OPNFV_ARTIFACT_VERSION $NOCACHE_ARG -c file://$CACHE_DIRECTORY $BUILD_DIRECTORY

# list the build artifacts
ls -al $BUILD_DIRECTORY

# save information regarding artifact into file
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
    echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
    echo "OPNFV_ARTIFACT_URL=$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
    echo "OPNFV_ARTIFACT_SHA512SUM=$(sha512sum $BUILD_DIRECTORY/opnfv-$OPNFV_ARTIFACT_VERSION.iso | cut -d' ' -f1)"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
) > $WORKSPACE/opnfv.properties

echo
echo "--------------------------------------------------------"
echo "Done!"
