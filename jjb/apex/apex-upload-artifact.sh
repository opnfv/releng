#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

if [ -z "$ARTIFACT_TYPE" ]; then
  echo "ERROR: ARTIFACT_TYPE not provided...exiting"
  exit 1
fi

# log info to console
echo "Uploading the Apex ${ARTIFACT_TYPE} artifact. This could take some time..."
echo "--------------------------------------------------------"
echo

# source the opnfv.properties to get ARTIFACT_VERSION
source $WORKSPACE/opnfv.properties

BUILD_DIRECTORY=${WORKSPACE}/.build

# clone releng repository
echo "Cloning releng repository..."
[ -d releng ] && rm -rf releng
git clone https://gerrit.opnfv.org/gerrit/releng $WORKSPACE/releng/ &> /dev/null
#this is where we import the siging key
if [ -f $WORKSPACE/releng/utils/gpg_import_key.sh ]; then
  source $WORKSPACE/releng/utils/gpg_import_key.sh
fi

signrpm () {
for artifact in $RPM_LIST $SRPM_LIST; do
  echo "Signing artifact: ${artifact}"
  gpg2 -vvv --batch --yes --no-tty \
    --default-key opnfv-helpdesk@rt.linuxfoundation.org \
    --passphrase besteffort \
    --detach-sig $artifact
    gsutil cp "$artifact".sig gs://$GS_URL/$(basename "$artifact".sig)
    echo "Upload complete for ${artifact} signature"
done
}

signiso () {
time gpg2 -vvv --batch --yes --no-tty \
  --default-key opnfv-helpdesk@rt.linuxfoundation.org  \
  --passphrase besteffort \
  --detach-sig $BUILD_DIRECTORY/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso

gsutil cp $BUILD_DIRECTORY/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso.sig gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso.sig 
echo "ISO signature Upload Complete!"
}

uploadiso () {
  gsutil cp $BUILD_DIRECTORY/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso > gsutil.iso.log
  echo "ISO Upload Complete!"
}

uploadrpm () {
  for artifact in $RPM_LIST $SRPM_LIST; do
    echo "Uploading artifact: ${artifact}"
    gsutil cp $artifact gs://$GS_URL/$(basename $artifact) > gsutil.iso.log
    echo "Upload complete for ${artifact}"
  done
  gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log
  gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/latest.properties > gsutil.latest.log
}

uploadsnap () {
  # Uploads snapshot artifact and updated properties file
  echo "Uploading snapshot artifacts"
  SNAP_TYPE=$(echo ${JOB_NAME} | sed -n 's/^apex-\(.\+\)-promote.*$/\1/p')
  gsutil cp $WORKSPACE/apex-${SNAP_TYPE}-snap-`date +%Y-%m-%d`.tar.gz gs://$GS_URL/ > gsutil.iso.log
  if [ "$SNAP_TYPE" == 'csit' ]; then
    gsutil cp $WORKSPACE/snapshot.properties gs://$GS_URL/snapshot.properties > gsutil.latest.log
  fi
  echo "Upload complete for Snapshot"
}

if gpg2 --list-keys | grep "opnfv-helpdesk@rt.linuxfoundation.org"; then
  echo "Signing Key avaliable"
  SIGN_ARTIFACT="true"
fi

if [ "$ARTIFACT_TYPE" == 'snapshot' ]; then
  uploadsnap
elif [ "$ARTIFACT_TYPE" == 'iso' ]; then
  if [[ -n "$SIGN_ARTIFACT" && "$SIGN_ARTIFACT" == "true" ]]; then
    signiso
  fi
  uploadiso
elif [ "$ARTIFACT_TYPE" == 'rpm' ]; then
  RPM_INSTALL_PATH=$BUILD_DIRECTORY/noarch
  RPM_LIST=$RPM_INSTALL_PATH/$(basename $OPNFV_RPM_URL)
  VERSION_EXTENSION=$(echo $(basename $OPNFV_RPM_URL) | sed 's/opnfv-apex-//')
  for pkg in common undercloud; do # removed onos for danube
    RPM_LIST+=" ${RPM_INSTALL_PATH}/opnfv-apex-${pkg}-${VERSION_EXTENSION}"
  done
  SRPM_INSTALL_PATH=$BUILD_DIRECTORY
  SRPM_LIST=$SRPM_INSTALL_PATH/$(basename $OPNFV_SRPM_URL)
  VERSION_EXTENSION=$(echo $(basename $OPNFV_SRPM_URL) | sed 's/opnfv-apex-//')
  for pkg in common undercloud; do # removed onos for danube
    SRPM_LIST+=" ${SRPM_INSTALL_PATH}/opnfv-apex-${pkg}-${VERSION_EXTENSION}"
  done

  if [[ -n "$SIGN_ARTIFACT" && "$SIGN_ARTIFACT" == "true" ]]; then
    signrpm
  fi
  uploadrpm
else
  echo "ERROR: Unknown artifact type ${ARTIFACT_TYPE} to upload...exiting"
  exit 1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"
if [ "$ARTIFACT_TYPE" == 'iso' ]; then echo "ISO Artifact is available as http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"; fi
if [ "$ARTIFACT_TYPE" == 'rpm' ]; then echo "RPM Artifact is available as http://$GS_URL/$(basename $OPNFV_RPM_URL)"; fi
