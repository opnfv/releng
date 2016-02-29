#!/bin/bash
set -o nounset
set -o pipefail

# log info to console
echo "Uploading the $INSTALLER_TYPE artifact. This could take some time..."
echo "--------------------------------------------------------"
echo

# source the opnfv.properties to get ARTIFACT_VERSION
source $BUILD_DIRECTORY/opnfv.properties

# upload artifact and additional files to google storage
gsutil cp $BUILD_DIRECTORY/compass.iso gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso > gsutil.iso.log 2>&1
gsutil cp $BUILD_DIRECTORY/opnfv.properties gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log 2>&1
gsutil cp $BUILD_DIRECTORY/opnfv.properties gs://$GS_URL/latest.properties > gsutil.latest.log 2>&1

gsutil -m setmeta \
    -h "Content-Type:text/html" \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/latest.properties \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > /dev/null 2>&1

gsutil -m setmeta \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso > /dev/null 2>&1

# disabled errexit due to gsutil setmeta complaints
#   BadRequestException: 400 Invalid argument
# check if we uploaded the file successfully to see if things are fine
gsutil ls gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Problem while uploading artifact!"
    echo "Check log $WORKSPACE/gsutil.iso.log on the machine where this build is done."
    exit 1

else
  gsutil cp gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso \
    gs://$GS_URL/opnfv-latest.iso

  gsutil -m setmeta \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/opnfv-latest.iso > /dev/null 2>&1
fi


echo
echo "--------------------------------------------------------"
echo "Done!"
echo "Artifact is available as http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
