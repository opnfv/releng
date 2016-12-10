#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

echo "Building Gluon packages."
echo "------------------------"
echo

if [ "$ARTIFACT_VERSION" == "daily" ]; then
   export OPNFV_ARTIFACT_VERSION=$(echo $(date -u +"%Y%m%d"))
fi

# build all packages
cd $WORKSPACE/ci
./build-gluon-packages.sh

# list the contents of BUILD_OUTPUT directory
echo "Build Directory is ${BUILD_DIRECTORY}"
echo "Build Directory Contents:"
echo "---------------------------------------"
ls -alR $BUILD_DIRECTORY

# get version infos from Gluon from spec
GLUON_VERSION=$(grep Version: $BUILD_DIRECTORY/rpm_specs/gluon.spec | awk '{ print $2 }')
GLUON_RELEASE=$(grep 'define release' $BUILD_DIRECTORY/rpm_specs/gluon.spec | awk '{ print $3 }')_$OPNFV_ARTIFACT_VERSION

ARTIFACT_NAME=gluon-$GLUON_VERSION-$GLUON_RELEASE.noarch.rpm
ARTIFACT_PATH=$BUILD_DIRECTORY/noarch/$ARTIFACT_NAME

echo "Writing opnfv.properties file"
# save information regarding artifact into file
(
  echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
  echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
  echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
  echo "OPNFV_ARTIFACT_URL=$GS_URL/$ARTIFACT_NAME"
  echo "OPNFV_ARTIFACT_SHA512SUM=$(sha512sum $ARTIFACT_PATH | cut -d' ' -f1)"
  echo "OPNFV_BUILD_URL=$BUILD_URL"
  echo "ARTIFACT_LIST=$ARTIFACT_PATH"
) > $WORKSPACE/opnfv.properties

echo "---------------------------------------"
echo "Done!"
