#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

echo "--------------------------------------------------------"
echo "This is diasy4nfv build job!"
echo "--------------------------------------------------------"

# set OPNFV_ARTIFACT_VERSION
if [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Building Daisy4nfv ISO for a merged change"
    export OPNFV_ARTIFACT_VERSION="gerrit-$GERRIT_CHANGE_NUMBER"
else
    export OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
fi

# build output directory
OUTPUT_DIR=$WORKSPACE/build_output
mkdir -p $OUTPUT_DIR

# start the build
cd $WORKSPACE
./ci/build.sh $OUTPUT_DIR $OPNFV_ARTIFACT_VERSION

# save information regarding artifact into file
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
    echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
    echo "OPNFV_ARTIFACT_URL=$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.bin"
    echo "OPNFV_ARTIFACT_SHA512SUM=$(sha512sum $OUTPUT_DIR/opnfv-$OPNFV_ARTIFACT_VERSION.bin | cut -d' ' -f1)"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
) > $WORKSPACE/opnfv.properties

echo
echo "--------------------------------------------------------"
echo "Done!"
