#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

ODL_ZIP=distribution-karaf-0.6.0-SNAPSHOT.zip

echo "Attempting to fetch the artifact location from ODL Jenkins"
CHANGE_DETAILS_URL="https://git.opendaylight.org/gerrit/changes/netvirt~master~$GERRIT_CHANGE_ID/detail"
# due to limitation with the Jenkins Gerrit Trigger, we need to use Gerrit REST API to get the change details
ODL_BUILD_JOB_NUM=$(curl -s $CHANGE_DETAILS_URL | grep -Eo 'netvirt-distribution-check-nitrogen/[0-9]+' | tail -1 | grep -Eo [0-9]+)
DISTRO_CHECK_CONSOLE_LOG="https://logs.opendaylight.org/releng/jenkins092/netvirt-distribution-check-nitrogen/${ODL_BUILD_JOB_NUM}/console.log.gz"
NETVIRT_ARTIFACT_URL=$(curl -s --compressed $DISTRO_CHECK_CONSOLE_LOG | grep 'BUNDLE_URL' | cut -d = -f 2)

echo -e "URL to artifact is\n\t$NETVIRT_ARTIFACT_URL"

echo "Downloading the artifact. This could take time..."
wget -q -O $ODL_ZIP $NETVIRT_ARTIFACT_URL
if [[ $? -ne 0 ]]; then
    echo "The artifact does not exist! Probably removed due to ODL Jenkins artifact retention policy."
    echo "Rerun netvirt-patch-test-current-carbon to get artifact rebuilt."
    exit 1
fi

#TODO(trozet) remove this once odl-pipeline accepts zip files
echo "Converting artifact zip to tar.gz"
unzip $ODL_ZIP
tar czf /tmp/${NETVIRT_ARTIFACT} $(echo $ODL_ZIP | sed -n 's/\.zip//p')

echo "Download complete"
ls -al /tmp/${NETVIRT_ARTIFACT}