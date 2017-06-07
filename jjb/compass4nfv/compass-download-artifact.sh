#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Downloading the $INSTALLER_TYPE artifact. This could take some time..."
echo "--------------------------------------------------------"
echo

# get the latest.properties file in order to get info regarding latest artifact
[[ -d $BUILD_DIRECTORY ]] || mkdir -p $BUILD_DIRECTORY
curl -s -o $BUILD_DIRECTORY/latest.properties http://$GS_URL/latest.properties

# check if we got the file
[[ -f $BUILD_DIRECTORY/latest.properties ]] || exit 1

# source the file so we get OPNFV vars
source $BUILD_DIRECTORY/latest.properties

if [[ "$BRANCH" == 'stable/danube' ]]; then
    # download the file
    curl -s -o $BUILD_DIRECTORY/compass.iso http://$OPNFV_ARTIFACT_URL > gsutil.iso.log 2>&1
    # list the file
    ls -al $BUILD_DIRECTORY/compass.iso
else
    # download the file
    curl -s -o $BUILD_DIRECTORY/compass.tar.gz http://$OPNFV_ARTIFACT_URL > gsutil.tar.gz.log 2>&1
    # list the file
    ls -al $BUILD_DIRECTORY/compass.tar.gz
fi

echo
echo "--------------------------------------------------------"
echo "Done!"
