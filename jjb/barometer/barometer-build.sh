set -x

OPNFV_BRANCH=$BRANCH
OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
OPNFV_ARTIFACT_URL="$GS_URL/$OPNFV_BRANCH/$OPNFV_ARTIFACT_VERSION/"

# log info to console
echo "Starting the build of Barometer RPMs"
echo "------------------------------------"
echo

cd ci
./install_dependencies.sh
./build_rpm.sh
cd $WORKSPACE

# save information regarding artifact into file
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_ARTIFACT_URL=$OPNFV_ARTIFACT_URL"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
) > $BUILD_DIRECTORY/opnfv.properties

