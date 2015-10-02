#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# get the latest.properties file in order to get info regarding latest artifact
curl -s -o $WORKSPACE/latest.properties http://$GS_URL/latest.properties

# check if we got the file
[[ -f latest.properties ]] || exit 1

# source the file so we get OPNFV vars
source latest.properties

# log info to console
echo "Downloading the $INSTALLER artifact using URL http://$OPNFV_ARTIFACT_URL"
echo "This could take some time..."
echo "--------------------------------------------------------"
echo

# download the file
curl -s -o $WORKSPACE/opnfv.iso http://$OPNFV_ARTIFACT_URL > gsutil.iso.log 2>&1

# list the file
ls -al $WORKSPACE/opnfv.iso

echo
echo "--------------------------------------------------------"
echo "Done!"
