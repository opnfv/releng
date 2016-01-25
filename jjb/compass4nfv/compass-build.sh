#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
set -x

# log info to console
echo "Starting the build of $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

# create the cache directory if it doesn't exist
[[ -d $CACHE_DIRECTORY ]] || mkdir -p $CACHE_DIRECTORY
[[ -d $BUILD_DIRECTORY ]] || mkdir -p $BUILD_DIRECTORY

# set OPNFV_ARTIFACT_VERSION
export OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
export PACKAGE_URL=$PPA_REPO

# start the build
if [ -d $PPA_CACHE ]
then
    cp $PPA_CACHE/*.tar.gz $PPA_CACHE/*.iso $PPA_CACHE/*.img $CACHE_DIRECTORY/ -f
fi

cd $WORKSPACE/
./build.sh  --iso-dir $BUILD_DIRECTORY/ --iso-name compass.iso -c $CACHE_DIRECTORY

# list the build artifacts
ls -al $BUILD_DIRECTORY

# save information regarding artifact into file
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
    echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
    echo "OPNFV_ARTIFACT_URL=$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
    echo "OPNFV_ARTIFACT_MD5SUM=$(md5sum $BUILD_DIRECTORY/compass.iso | cut -d' ' -f1)"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
) > $BUILD_DIRECTORY/opnfv.properties
echo
echo "--------------------------------------------------------"
echo "Done!"
