#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Uploading the Apex artifact. This could take some time..."
echo "--------------------------------------------------------"
echo

# source the opnfv.properties to get ARTIFACT_VERSION
source $WORKSPACE/opnfv.properties

# clone releng repository
echo "Cloning releng repository..."
[ -d releng ] && rm -rf releng
git clone https://gerrit.opnfv.org/gerrit/releng &> /dev/null
#this is where we import the siging key
source $WORKSPACE/releng/utils/gpg_import_key.sh

signrpm () {
for artifact in $RPM_LIST $SRPM_LIST; do
  echo "Signing artifact: ${artifact}"
  gpg2 -vvv --batch \
    --default-key opnfv-helpdesk@rt.linuxfoundation.org  \
    --passphrase besteffort \
    --detach-sig $artifact
    gsutil cp "$artifact".sig gs://$GS_URL/$(basename "$artifact".sig)
    echo "Upload complete for ${artifact} signature"
done
}

signiso () {
time gpg2 -vvv --batch \
  --default-key opnfv-helpdesk@rt.linuxfoundation.org  \
  --passphrase notreallysecure \
  --detach-sig $BUILD_DIRECTORY/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso

gsutil cp $BUILD_DIRECTORY/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso.sig gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso.sig 
echo "ISO signature Upload Complete!"
}

uploadiso () {
# upload artifact and additional files to google storage
gsutil cp $BUILD_DIRECTORY/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso > gsutil.iso.log
echo "ISO Upload Complete!"
RPM_INSTALL_PATH=$BUILD_DIRECTORY/noarch
RPM_LIST=$RPM_INSTALL_PATH/$(basename $OPNFV_RPM_URL)
VERSION_EXTENSION=$(echo $(basename $OPNFV_RPM_URL) | sed 's/opnfv-apex-//')
for pkg in common undercloud opendaylight-sfc onos; do
    RPM_LIST+=" ${RPM_INSTALL_PATH}/opnfv-apex-${pkg}-${VERSION_EXTENSION}"
done
SRPM_INSTALL_PATH=$BUILD_DIRECTORY
SRPM_LIST=$SRPM_INSTALL_PATH/$(basename $OPNFV_SRPM_URL)
VERSION_EXTENSION=$(echo $(basename $OPNFV_SRPM_URL) | sed 's/opnfv-apex-//')
for pkg in common undercloud opendaylight-sfc onos; do
    SRPM_LIST+=" ${SRPM_INSTALL_PATH}/opnfv-apex-${pkg}-${VERSION_EXTENSION}"
done
}

uploadrpm () {
#This is where we upload the rpms
for artifact in $RPM_LIST $SRPM_LIST; do
  echo "Uploading artifact: ${artifact}"
  gsutil cp $artifact gs://$GS_URL/$(basename $artifact) > gsutil.iso.log
  echo "Upload complete for ${artifact}"
done
gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log
gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/latest.properties > gsutil.latest.log
}

if gpg2 --list-keys | grep "opnfv-helpdesk@rt.linuxfoundation.org"; then
  echo "Signing Key avaliable"
  signiso
  uploadiso
  signrpm
  uploadrpm
else
  uploadiso
  uploadrpm
fi

echo
echo "--------------------------------------------------------"
echo "Done!"
echo "ISO Artifact is available as http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
echo "RPM Artifact is available as http://$GS_URL/$(basename $OPNFV_RPM_URL)"
