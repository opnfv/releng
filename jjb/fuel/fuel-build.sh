#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Starting the build of $INSTALLER. This could take some time..."
echo "--------------------------------------------------------"
echo

# create the cache directory if it doesn't exist
[[ -d $CACHE_DIRECTORY ]] || mkdir -p $CACHE_DIRECTORY

# set OPNFV_ARTIFACT_VERSION
if [[ $GERRIT_EVENT_TYPE = "change-merged" ]]; then
    echo "Building Fuel ISO for a merged change"
    OPNFV_ARTIFACT_VERSION=$(gerrit-$GERRIT_CHANGE_NUMBER)
else
    OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
fi

# start the build
cd $WORKSPACE/$INSTALLER/ci
./build.sh -v $OPNFV_ARTIFACT_VERSION -c file://$CACHE_DIRECTORY $BUILD_DIRECTORY

# list the build artifacts
ls -al $BUILD_DIRECTORY

# save information regarding artifact into file
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
    echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
    echo "OPNFV_ARTIFACT_URL=$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
    echo "OPNFV_ARTIFACT_MD5SUM=$(md5sum $BUILD_DIRECTORY/opnfv-$OPNFV_ARTIFACT_VERSION.iso | cut -d' ' -f1)"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
) > $WORKSPACE/opnfv.properties

echo
echo "--------------------------------------------------------"
echo "Done!"
