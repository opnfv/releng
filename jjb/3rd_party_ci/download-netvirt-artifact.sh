#!/bin/bash

echo "Attempting to fetch the artifact location from ODL Jenkins"
CHANGE_DETAILS_URL="https://git.opendaylight.org/gerrit/changes/netvirt~master~$GERRIT_CHANGE_ID/detail"
# due to limitation with the Jenkins Gerrit Trigger, we need to use Gerrit REST API to get the change details
ODL_JOB_URL=$(curl -s $CHANGE_DETAILS_URL | grep netvirt-patch-test-current-carbon | tail -1 | \
    sed 's/\\n//g' | awk '{print $6}')
NETVIRT_ARTIFACT_URL="${ODL_JOB_URL}org.opendaylight.integration\$distribution-karaf/artifact/org.opendaylight.integration/distribution-karaf/0.6.0-SNAPSHOT/distribution-karaf-0.6.0-SNAPSHOT.tar.gz"
echo -e "URL to artifact is\n\t$NETVIRT_ARTIFACT_URL"
echo "Downloading the artifact. This could take time..."
curl -s -o $NETVIRT_ARTIFACT $NETVIRT_ARTIFACT_URL
echo "Download complete"
ls -al $NETVIRT_ARTIFACT
