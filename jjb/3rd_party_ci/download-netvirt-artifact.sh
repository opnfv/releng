#!/bin/bash
set -e

# wipe the WORKSPACE
/bin/rm -rf $WORKSPACE/*

echo "Attempting to fetch the artifact location from ODL Jenkins"
CHANGE_DETAILS_URL="https://git.opendaylight.org/gerrit/changes/netvirt~master~$GERRIT_CHANGE_ID/detail"
# due to limitation with the Jenkins Gerrit Trigger, we need to use Gerrit REST API to get the change details
ODL_JOB_URL=$(curl -s $CHANGE_DETAILS_URL | grep netvirt-patch-test-current-carbon | tail -1 | \
    sed 's/\\n//g' | awk '{print $6}')
NETVIRT_ARTIFACT_URL="${ODL_JOB_URL}org.opendaylight.integration\$distribution-karaf/artifact/org.opendaylight.integration/distribution-karaf/0.6.0-SNAPSHOT/distribution-karaf-0.6.0-SNAPSHOT.tar.gz"
echo -e "URL to artifact is\n\t$NETVIRT_ARTIFACT_URL"

echo "Downloading the artifact. This could take time..."
wget -q -O $NETVIRT_ARTIFACT $NETVIRT_ARTIFACT_URL
if [[ $? -ne 0 ]]; then
    echo "The artifact does not exist! Probably removed due to ODL Jenkins artifact retention policy."
    echo "Rerun netvirt-patch-test-current-carbon to get artifact rebuilt."
    exit 1
fi
echo "Download complete"
ls -al $NETVIRT_ARTIFACT
