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

if [[ ! "$ARTIFACT_VERSION" =~ dev ]]; then
  source $BUILD_DIRECTORY/../opnfv.properties
fi

importkey () {
  # clone releng repository
  echo "Cloning releng repository..."
  [ -d releng ] && rm -rf releng
  git clone https://gerrit.opnfv.org/gerrit/releng $WORKSPACE/releng/ &> /dev/null
  #this is where we import the siging key
  if [ -f $WORKSPACE/releng/utils/gpg_import_key.sh ]; then
    source $WORKSPACE/releng/utils/gpg_import_key.sh
  fi
}

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
  gpg2 -vvv --batch --yes --no-tty \
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

  # Make the property files viewable on the artifact site
  gsutil -m setmeta \
    -h "Content-Type:text/html" \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/latest.properties \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > /dev/null 2>&1
}

uploadsnap () {
  # Uploads snapshot artifact and updated properties file
  echo "Uploading snapshot artifacts"
  if [ -z "$SNAP_TYPE" ]; then
    echo "ERROR: SNAP_TYPE not provided...exiting"
    exit 1
  fi
  gsutil cp $WORKSPACE/apex-${SNAP_TYPE}-snap-`date +%Y-%m-%d`.tar.gz gs://$GS_URL/ > gsutil.iso.log
  if [ "$SNAP_TYPE" == 'csit' ]; then
    gsutil cp $WORKSPACE/snapshot.properties gs://$GS_URL/snapshot.properties > gsutil.latest.log
  fi
  echo "Upload complete for Snapshot"
}

uploadimages () {
  # Uploads dev tarball
  GERRIT_PATCHSET_NUMBER=$(echo $GERRIT_REFSPEC | grep -Eo '[0-9]+$')
  export OPNFV_ARTIFACT_VERSION="dev${GERRIT_CHANGE_NUMBER}_${GERRIT_PATCHSET_NUMBER}"
  echo "Uploading development build tarball"
  pushd $BUILD_DIRECTORY > /dev/null
  tar czf apex-${OPNFV_ARTIFACT_VERSION}.tar.gz *.qcow2 *.vmlinuz *.initrd
  gsutil cp apex-${OPNFV_ARTIFACT_VERSION}.tar.gz gs://$GS_URL/apex-${OPNFV_ARTIFACT_VERSION}.tar.gz > gsutil.latest.log
  popd > /dev/null
}

# Always import the signing key, if it's available the artifacts will be
# signed before being uploaded
importkey

if gpg2 --list-keys | grep "opnfv-helpdesk@rt.linuxfoundation.org"; then
  echo "Signing Key avaliable"
  SIGN_ARTIFACT="true"
fi

if [ "$ARTIFACT_TYPE" == 'snapshot' ]; then
  uploadsnap
elif [ "$ARTIFACT_TYPE" == 'iso' ]; then
  if [[ "$ARTIFACT_VERSION" =~ dev ]]; then
    echo "Skipping artifact upload for ${ARTIFACT_TYPE} due to dev build"
    exit 0
  fi
  if [[ -n "$SIGN_ARTIFACT" && "$SIGN_ARTIFACT" == "true" ]]; then
    signiso
  fi
  uploadiso
elif [ "$ARTIFACT_TYPE" == 'rpm' ]; then
  if [[ "$ARTIFACT_VERSION" =~ dev ]]; then
    echo "dev build detected, will upload image tarball"
    ARTIFACT_TYPE=tarball
    uploadimages
  else
    RPM_INSTALL_PATH=$BUILD_DIRECTORY/noarch
    RPM_LIST=$RPM_INSTALL_PATH/$(basename $OPNFV_RPM_URL)
    VERSION_EXTENSION=$(echo $(basename $OPNFV_RPM_URL) | sed 's/opnfv-apex-//')
    for pkg in common undercloud onos; do
      RPM_LIST+=" ${RPM_INSTALL_PATH}/opnfv-apex-${pkg}-${VERSION_EXTENSION}"
    done
    SRPM_INSTALL_PATH=$BUILD_DIRECTORY
    SRPM_LIST=$SRPM_INSTALL_PATH/$(basename $OPNFV_SRPM_URL)
    VERSION_EXTENSION=$(echo $(basename $OPNFV_SRPM_URL) | sed 's/opnfv-apex-//')
    for pkg in common undercloud onos; do
      SRPM_LIST+=" ${SRPM_INSTALL_PATH}/opnfv-apex-${pkg}-${VERSION_EXTENSION}"
    done

    if [[ -n "$SIGN_ARTIFACT" && "$SIGN_ARTIFACT" == "true" ]]; then
      signrpm
    fi
    uploadrpm
  fi
else
  echo "ERROR: Unknown artifact type ${ARTIFACT_TYPE} to upload...exiting"
  exit 1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"
if [ "$ARTIFACT_TYPE" == 'iso' ]; then echo "ISO Artifact is available as http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"; fi
if [ "$ARTIFACT_TYPE" == 'rpm' ]; then echo "RPM Artifact is available as http://$GS_URL/$(basename $OPNFV_RPM_URL)"; fi
if [ "$ARTIFACT_TYPE" == 'tarball' ]; then echo "Dev tarball Artifact is available as http://$GS_URL/apex-${OPNFV_ARTIFACT_VERSION}.tar.gz)"; fi
