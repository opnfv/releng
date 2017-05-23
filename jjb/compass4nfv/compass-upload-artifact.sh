#!/bin/bash
set -o nounset
set -o pipefail

# log info to console
echo "Uploading the $INSTALLER_TYPE artifact. This could take some time..."
echo "--------------------------------------------------------"
echo

if [[ "$BRANCH" == 'danube' ]]; then
    FILETYPE='iso'
else
    FILETYPE='tar.gz'
fi
# source the opnfv.properties to get ARTIFACT_VERSION
source $BUILD_DIRECTORY/opnfv.properties

# clone releng repository
echo "Cloning releng repository..."
[ -d releng ] && rm -rf releng
git clone https://gerrit.opnfv.org/gerrit/releng $WORKSPACE/releng/ &> /dev/null
#this is where we import the siging key
if [ -f $WORKSPACE/releng/utils/gpg_import_key.sh ]; then
  source $WORKSPACE/releng/utils/gpg_import_key.sh
fi

signiso () {
time gpg2 -vvv --batch --yes --no-tty \
  --default-key opnfv-helpdesk@rt.linuxfoundation.org  \
  --passphrase besteffort \
  --detach-sig $BUILD_DIRECTORY/compass.$FILETYPE

gsutil cp $BUILD_DIRECTORY/compass.$FILETYPE.sig gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.$FILETYPE.sig
echo "ISO signature Upload Complete!"
}

signiso

# upload artifact and additional files to google storage
gsutil cp $BUILD_DIRECTORY/compass.$FILETYPE gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.$FILETYPE > gsutil.$FILETYPE.log 2>&1
gsutil cp $BUILD_DIRECTORY/opnfv.properties gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log 2>&1
gsutil cp $BUILD_DIRECTORY/opnfv.properties gs://$GS_URL/latest.properties > gsutil.latest.log 2>&1

gsutil -m setmeta \
    -h "Content-Type:text/html" \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/latest.properties \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > /dev/null 2>&1

gsutil -m setmeta \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.$FILETYPE > /dev/null 2>&1

# disabled errexit due to gsutil setmeta complaints
#   BadRequestException: 400 Invalid argument
# check if we uploaded the file successfully to see if things are fine
gsutil ls gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.$FILETYPE > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Problem while uploading artifact!"
    echo "Check log $WORKSPACE/gsutil.$FILETYPE.log on the machine where this build is done."
    exit 1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"
echo "Artifact is available as http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.$FILETYPE"
