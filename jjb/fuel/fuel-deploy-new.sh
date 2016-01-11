#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# source the file so we get OPNFV vars
source latest.properties

# echo the info about artifact that is used during the deployment
echo "Using $(echo $OPNFV_ARTIFACT_URL | cut -d'/' -f3) for deployment"

# checkout the commit that was used for building the downloaded artifact
# to make sure the ISO and deployment mechanism uses same versions
#echo "Checking out $OPNFV_GIT_SHA1"
#git checkout $OPNFV_GIT_SHA1 --quiet

# set deployment parameters
BRIDGE=pxebr
export TMPDIR=$HOME/tmpdir
LAB_NAME=${NODE_NAME/-*}
POD_NAME=${NODE_NAME/*-}

# create TMPDIR if it doesn't exist
mkdir -p $TMPDIR

# change permissions down to TMPDIR
chmod a+x $HOME
chmod a+x $TMPDIR

# clone the securedlab repo
cd $WORKSPACE
echo "Cloning securedlab repo"
git clone ssh://jenkins-ericsson@gerrit.opnfv.org:29418/securedlab

# construct the command
DEPLOY_COMMAND="sudo $WORKSPACE/ci/deploy.sh -b file://$WORKSPACE/securedlab -l $LAB_NAME -p $POD_NAME -s $DEPLOY_SCENARIO -i $WORKSPACE/opnfv.iso -H -B $BRIDGE  -S $TMPDIR"

# log info to console
echo "Deployment parameters"
echo "Scenario: $DEPLOY_SCENARIO"
echo "--------------------------------------------------------"
echo "Lab: $LAB_NAME"
echo "POD: $POD_NAME"
echo "ISO: $(echo $OPNFV_ARTIFACT_URL | cut -d'/' -f3)"
echo
echo "Starting the deployment using $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

# start the deployment
echo "Issuing command"
echo "$DEPLOY_COMMAND"
echo

$DEPLOY_COMMAND

echo
echo "--------------------------------------------------------"
echo "Done!"
