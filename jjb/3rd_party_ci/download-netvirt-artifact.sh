#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

echo "Attempting to fetch the artifact location from ODL Jenkins"
CHANGE_DETAILS_URL="https://git.opendaylight.org/gerrit/changes/netvirt~master~$GERRIT_CHANGE_ID/detail"
# due to limitation with the Jenkins Gerrit Trigger, we need to use Gerrit REST API to get the change details
ODL_BUILD_JOB_NUM=$(curl -s $CHANGE_DETAILS_URL | grep -Eo 'netvirt-distribution-check-carbon/[0-9]+' | tail -1 | grep -Eo [0-9]+)

NETVIRT_ARTIFACT_URL="https://jenkins.opendaylight.org/releng/job/netvirt-distribution-check-carbon/${ODL_BUILD_JOB_NUM}/artifact/distribution-karaf-0.6.0-SNAPSHOT.zip"
echo -e "URL to artifact is\n\t$NETVIRT_ARTIFACT_URL"

echo "Downloading the artifact. This could take time..."
wget -q -O distribution-karaf-0.6.0-SNAPSHOT.zip $NETVIRT_ARTIFACT_URL
if [[ $? -ne 0 ]]; then
    echo "The artifact does not exist! Probably removed due to ODL Jenkins artifact retention policy."
    echo "Rerun netvirt-patch-test-current-carbon to get artifact rebuilt."
    exit 1
fi

#TODO(trozet) remove this once odl-pipeline accepts zip files
echo "Converting artifact zip to tar.gz"
sudo pip install ruamel.zip2tar
zip2tar distribution-karaf-0.6.0-SNAPSHOT.zip --gz --tar-file-name /tmp/${NETVIRT_ARTIFACT}

echo "Download complete"
ls -al /tmp/${NETVIRT_ARTIFACT}
