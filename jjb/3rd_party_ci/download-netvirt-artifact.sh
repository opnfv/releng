#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

echo "Attempting to fetch the artifact location from ODL Jenkins"
if [ "$ODL_BRANCH" != 'master' ]; then
  DIST=$(echo ${ODL_BRANCH} | sed -rn 's#([a-zA-Z]+)/([a-zA-Z]+)#\2#p')
  ODL_BRANCH=$(echo ${ODL_BRANCH} | sed -rn 's#([a-zA-Z]+)/([a-zA-Z]+)#\1%2F\2#p')
else
  DIST='fluorine'
fi

echo "ODL Distribution is ${DIST}"
ODL_ZIP="karaf-SNAPSHOT.zip"
CHANGE_DETAILS_URL="https://git.opendaylight.org/gerrit/changes/netvirt~${ODL_BRANCH}~${GERRIT_CHANGE_ID}/detail"
# due to limitation with the Jenkins Gerrit Trigger, we need to use Gerrit REST API to get the change details
ODL_BUILD_JOB_NUM=$(curl --fail ${CHANGE_DETAILS_URL} | grep -Eo "netvirt-distribution-check-${DIST}/[0-9]+" | tail -1 | grep -Eo [0-9]+)
DISTRO_CHECK_CONSOLE_LOG="https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1/netvirt-distribution-check-${DIST}/${ODL_BUILD_JOB_NUM}/console.log.gz"
NETVIRT_ARTIFACT_URL=$(curl --fail --compressed ${DISTRO_CHECK_CONSOLE_LOG} | grep 'BUNDLE_URL' | cut -d = -f 2)

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
UNZIPPED_DIR=`dirname $(unzip -qql ${ODL_ZIP} | head -n1 | tr -s ' ' | cut -d' ' -f5-)`
unzip ${ODL_ZIP}
tar czf /tmp/${NETVIRT_ARTIFACT} ${UNZIPPED_DIR}

echo "Download complete"
ls -al /tmp/${NETVIRT_ARTIFACT}
