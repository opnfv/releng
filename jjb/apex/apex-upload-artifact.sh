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

for artifact in $RPM_LIST $SRPM_LIST; do
  echo "Uploading artifact: ${artifact}"
  gsutil cp $artifact gs://$GS_URL/$(basename $artifact) > gsutil.iso.log
  echo "Upload complete for ${artifact}"
done
gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log
gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/latest.properties > gsutil.latest.log

echo
echo "--------------------------------------------------------"
echo "Done!"
echo "ISO Artifact is available as http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
echo "RPM Artifact is available as http://$GS_URL/$(basename $OPNFV_RPM_URL)"
