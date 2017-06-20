#!/bin/bash
set -o nounset
set -o pipefail

RPM_WORKDIR=$WORKSPACE/rpmbuild
RPM_DIR=$RPM_WORKDIR/RPMS/x86_64/
cd $WORKSPACE/

# source the opnfv.properties to get ARTIFACT_VERSION
source $WORKSPACE/opnfv.properties

# upload property files
gsutil cp $WORKSPACE/opnfv.properties gs://$OPNFV_ARTIFACT_URL/opnfv.properties > gsutil.properties.log 2>&1
gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/latest.properties > gsutil.latest.log 2>&1

echo "Uploading the barometer RPMs to artifacts.opnfv.org"
echo "---------------------------------------------------"
echo

gsutil -m cp -r $RPM_DIR/* $OPNFV_ARTIFACT_URL > $WORKSPACE/gsutil.log 2>&1

# Check if the RPMs were pushed
gsutil ls $OPNFV_ARTIFACT_URL > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
  echo "Problem while uploading barometer RPMs to $OPNFV_ARTIFACT_URL!"
  echo "Check log $WORKSPACE/gsutil.log on the appropriate build server"
  exit 1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"
echo "Artifact is available at $OPNFV_ARTIFACT_URL"

gsutil -m setmeta \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$OPNFV_ARTIFACT_URL/*.rpm > /dev/null 2>&1

#cleanup the RPM repo from the build machine.
rm -rf $RPM_WORKDIR
