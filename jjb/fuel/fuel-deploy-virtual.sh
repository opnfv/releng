#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# source the file so we get OPNFV vars
source latest.properties

# echo the info about artifact that is used during the deployment
echo "Using $(echo $OPNFV_ARTIFACT_URL | cut -d'/' -f3) for deployment"

# create TMPDIR if it doesn't exist
export TMPDIR=$HOME/tmpdir
[[ -d $TMPDIR ]] || mkdir -p $TMPDIR

# change permissions down to TMPDIR
chmod a+x $HOME
chmod a+x $TMPDIR

# set CONFDIR, BRIDGE
CONFDIR=$WORKSPACE/deploy/templates/virtual_environment_noha/conf
BRIDGE=pxebr

# log info to console
echo "Starting the deployment for a merged change using $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

# start the deployment
echo "Issuing command"
echo "sudo $WORKSPACE/ci/deploy.sh -iso $WORKSPACE/opnfv.iso -dea $CONFDIR/dea.yaml -dha $CONFDIR/dha.yaml -s $TMPDIR -b $BRIDGE -nh"

sudo $WORKSPACE/ci/deploy.sh -iso $WORKSPACE/opnfv.iso -dea $CONFDIR/dea.yaml -dha $CONFDIR/dha.yaml -s $TMPDIR -b $BRIDGE -nh

echo
echo "--------------------------------------------------------"
echo "Virtual deployment is done! Removing the intermediate files from artifact repo"

PROPERTIES_FILE=$(echo $OPNFV_ARTIFACT_URL | sed 's/iso/properties/')
gsutil rm gs://$OPNFV_ARTIFACT_URL
gsutil rm gs://$PROPERTIES_FILE
