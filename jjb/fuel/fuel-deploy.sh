#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# source the file so we get OPNFV vars
source latest.properties

# echo the info about artifact that is used during the deployment
echo "Using ${OPNFV_ARTIFACT_URL/*\/} for deployment"

# checkout the commit that was used for building the downloaded artifact
# to make sure the ISO and deployment mechanism uses same versions
echo "Checking out $OPNFV_GIT_SHA1"
git checkout $OPNFV_GIT_SHA1 --quiet

# create TMPDIR if it doesn't exist
export TMPDIR=$HOME/tmpdir
mkdir -p $TMPDIR

# change permissions down to TMPDIR
chmod a+x $HOME
chmod a+x $TMPDIR

# set BRIDGE
BRIDGE=pxebr

# log info to console
echo "Starting the deployment using $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

# start the deployment
echo "Issuing command"
echo "sudo $WORKSPACE/ci/deploy.sh -iso $WORKSPACE/opnfv.iso -dea $POD_CONF_DIR/dea.yaml -dha $POD_CONF_DIR/dha.yaml -s $TMPDIR -b $BRIDGE -nh"

sudo $WORKSPACE/ci/deploy.sh -iso $WORKSPACE/opnfv.iso -dea $POD_CONF_DIR/dea.yaml -dha $POD_CONF_DIR/dha.yaml -s $TMPDIR -b $BRIDGE -nh

echo
echo "--------------------------------------------------------"
echo "Done!"
