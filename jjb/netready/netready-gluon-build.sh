#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

echo "Building Gluon packages."
echo "------------------------"
echo

if [ "$ARTIFACT_VERSION" == "daily" ]; then
   export OPNFV_ARTIFACT_VERSION=$(echo $(date -u +"%Y-%m-%d") | tr -d '_-')
fi

# build all packages
cd $WORKSPACE/ci
./build-gluon-packages.sh
./upload-gluon-packages.sh

# list the contents of BUILD_OUTPUT directory
echo "Build Directory is ${BUILD_DIRECTORY}"
echo "Build Directory Contents:"
echo "-------------------------"
ls -al $BUILD_DIRECTORY

echo "---------------------------------------"
echo "Done!"
