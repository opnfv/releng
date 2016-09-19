#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# 3. Check if dependencies exist in the cache, if yes, done
# 4. If not in cache, download the depdencies to the installer cache

# log info to console
echo "Downloading the $INSTALLER_TYPE artifact using URL http://$OPNFV_ARTIFACT_URL"
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

# Download the ISO and RPMs needed
curl -s -o $BUILD_DIRECTORY/apex.iso http://$OPNFV_ARTIFACT_URL > gsutil.iso.log 2>&1
curl -s -o $BUILD_DIRECTORY/$(basename $OPNFV_RPM_URL) http://$OPNFV_RPM_URL >> gsutil.iso.log 2>&1

# list the files
ls -al $BUILD_DIRECTORY

echo
echo "--------------------------------------------------------"
echo "Done!"
