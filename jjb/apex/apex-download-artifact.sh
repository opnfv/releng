#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

[[ -d $BUILD_DIRECTORY ]] || mkdir -p $BUILD_DIRECTORY

if [[ "$JOB_NAME" =~ verify ]]; then
  export OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
else
  export OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d")
fi

# get the properties file in order to get info regarding artifacts
curl -s -o $BUILD_DIRECTORY/opnfv.properties http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties

# check if we got the file
[[ -f $BUILD_DIRECTORY/opnfv.properties ]] || exit 1

# source the file so we get OPNFV vars
source $BUILD_DIRECTORY/opnfv.properties

# log info to console
echo "Downloading the $INSTALLER_TYPE artifact using URL http://$OPNFV_ARTIFACT_URL"
echo "--------------------------------------------------------"
echo

# Download the ISO and RPMs needed
curl -s -o $BUILD_DIRECTORY/apex.iso http://$OPNFV_ARTIFACT_URL > gsutil.iso.log 2>&1
curl -s -o $BUILD_DIRECTORY/$(basename $OPNFV_RPM_URL) http://$OPNFV_RPM_URL >> gsutil.iso.log 2>&1

# TODO: Uncomment these lines to verify SHA512SUMs once the sums are
# fixed.
# echo "$OPNFV_ARTIFACT_SHA512SUM $BUILD_DIRECTORY/apex.iso" | sha512sum -c
# echo "$OPNFV_RPM_SHA512SUM $BUILD_DIRECTORY/$(basename $OPNFV_RPM_URL)" | sha512sum -c

# list the files
ls -al $BUILD_DIRECTORY

echo
echo "--------------------------------------------------------"
echo "Done!"
