#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# 3. Check if dependencies exist in the cache, if yes, done
# 4. If not in cache, download the depdencies to the installer cache

# log info to console
echo "Downloading Apex artifacts. This could take some time..."
echo "--------------------------------------------------------"
echo

# /home/jenkins-ci/workspace/apex-deploy-***-**-***/BUILD_DIRECTORY
# Previous builds at /home/jenkins-ci/workspace/BUILD_DIRECTORY

# get the latest.properties file in order to get info regarding latest artifact
[[ -d $BUILD_DIRECTORY ]] || mkdir -p $BUILD_DIRECTORY
curl -s -o $BUILD_DIRECTORY/opnfv.properties http://$GS_URL/latest.properties

# check if we got the file
[[ -f $BUILD_DIRECTORY/opnfv.properties ]] || exit 1

# source the file so we get OPNFV vars
source $BUILD_DIRECTORY/opnfv.properties

# Check if the artifact already exists
$OPNFV_ARTIFACT_VERSION

# download the file
curl -s -o $BUILD_DIRECTORY/apex.iso http://$OPNFV_ARTIFACT_URL > gsutil.iso.log 2>&1

# list the file
ls -al $BUILD_DIRECTORY/apex.iso


if [[ "$JOB_NAME" =~ "verify" ]]; then
    # TODO: ALWAYS download the artifacts
    # Build is from a verify, use local build artifacts (not RPMs)
    cd $WORKSPACE/../${BUILD_DIRECTORY}
    WORKSPACE=$(pwd)
    echo "WORKSPACE modified to $WORKSPACE"
    cd $WORKSPACE/ci
elif [[ ! "$ARTIFACT_NAME" == "latest" ]]; then
    # if artifact name is passed the pull a
    # specific artifact from artifacts.opnfv.org
    # artifact specified should be opnfv-apex-<version>.noarch.rpm
    RPM_INSTALL_PATH=$GS_URL
    RPM_LIST=$RPM_INSTALL_PATH/$ARTIFACT_NAME
else
    # Use latest RPMS
    if [[ "$JOB_NAME" =~ "build" ]]; then
      # Triggered from a daily so RPMS should be in local directory
      # TODO: No, no they should not, the should have been downloaded
      BUILD_DIRECTORY=$WORKSPACE/../$BUILD_DIRECTORY
      echo "BUILD DIRECTORY modified to $BUILD_DIRECTORY"

      if [[ -f ${BUILD_DIRECTORY}/../opnfv.properties ]]; then
        # if opnfv.properties exists then use the
        # local build. Source the file so we get local OPNFV vars
        source ${BUILD_DIRECTORY}/../opnfv.properties
        RPM_INSTALL_PATH=${BUILD_DIRECTORY}/noarch
        RPM_LIST=$RPM_INSTALL_PATH/$(basename $OPNFV_RPM_URL)
      else
        # TODO: This should always pull the right properties file
        echo "BUILD_DIRECTORY is from a daily job, so will not use latest from URL"
        echo "Check that the slave has opnfv.properties in $BUILD_DIRECTORY"
        exit 1
      fi
    else
      # use the latest from artifacts.opnfv.org
      # get the latest.properties to get the link to the latest artifact
      curl -s -o $WORKSPACE/opnfv.properties http://$GS_URL/latest.properties

      # check if we got the file
      [[ -f $BUILD_DIRECTORY/opnfv.properties ]] || exit 1

      # source the file so we get OPNFV vars
      source opnfv.properties
      RPM_INSTALL_PATH=$(echo "http://"$OPNFV_RPM_URL | sed 's/\/'"$(basename $OPNFV_RPM_URL)"'//')
      RPM_LIST=${RPM_INSTALL_PATH}/$(basename $OPNFV_RPM_URL)
    fi
fi

echo
echo "--------------------------------------------------------"
echo "Done!"
