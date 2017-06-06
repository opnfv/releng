#!/bin/bash
set -o nounset
set -o pipefail

OPNFV_BRANCH=$BRANCH
OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
OPNFV_ARTIFACT_URL="$GS_URL/$OPNFV_BRANCH/$OPNFV_ARTIFACT_VERSION/"
RPM_WORKDIR=$WORKSPACE/rpmbuild

cd $WORKSPACE/

# source the opnfv.properties to get ARTIFACT_VERSION
source $BUILD_DIRECTORY/opnfv.properties

# upload property files
gsutil cp $BUILD_DIRECTORY/opnfv.properties gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log 2>&1
gsutil cp $BUILD_DIRECTORY/opnfv.properties gs://$GS_URL/$OPNFV_BRANCH/latest.properties > gsutil.latest.log 2>&1

echo "Uploading the barometer RPMs to artifacts.opnfv.org"
echo "---------------------------------------------------"
echo

gsutil -m cp -r $RPM_WORKDIR/RPMS/x86_64/* $OPNFV_ARTIFACT_URL > $WORKSPACE/gsutil.log 2>&1

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

#cleanup the RPM repo from the build machine.
rm -rf $RPM_WORKDIR
