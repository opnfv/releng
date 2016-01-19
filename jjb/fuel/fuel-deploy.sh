#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# source the file so we get OPNFV vars
source latest.properties

# echo the info about artifact that is used during the deployment
echo "Using ${OPNFV_ARTIFACT_URL/*\/} for deployment"

if [[ "$JOB_NAME" =~ "merge" ]]; then
    # set simplest scenario for virtual deploys to run for merges
    DEPLOY_SCENARIO="os-nosdn-nofeature-ha"
else
    # for none-merge deployments
    # checkout the commit that was used for building the downloaded artifact
    # to make sure the ISO and deployment mechanism uses same versions
    echo "Checking out $OPNFV_GIT_SHA1"
    git checkout $OPNFV_GIT_SHA1 --quiet
fi

# set deployment parameters
export TMPDIR=$HOME/tmpdir
BRIDGE=pxebr
LAB_NAME=${NODE_NAME/-*}
POD_NAME=${NODE_NAME/*-}

if [[ "$NODE_NAME" == "opnfv-jump-2" ]]; then
    LAB_NAME="lf"
    POD_NAME="pod2"
fi

if [[ "$NODE_NAME" =~ "virtual" ]]; then
    POD_NAME="virtual_kvm"
fi

# we currently support ericsson, intel, and lf labs
if [[ ! "$LAB_NAME" =~ (ericsson|intel|lf) ]]; then
    echo "Unsupported/unidentified lab $LAB_NAME. Cannot continue!"
    exit 1
else
    echo "Using configuration for $LAB_NAME"
fi

# create TMPDIR if it doesn't exist
export TMPDIR=$HOME/tmpdir
mkdir -p $TMPDIR

# change permissions down to TMPDIR
chmod a+x $HOME
chmod a+x $TMPDIR

# clone the securedlab repo
cd $WORKSPACE
echo "Cloning securedlab repo ${GIT_BRANCH##origin/}"
git clone ssh://jenkins-ericsson@gerrit.opnfv.org:29418/securedlab --quiet --branch ${GIT_BRANCH##origin/}

# construct the command
DEPLOY_COMMAND="sudo $WORKSPACE/ci/deploy.sh -b file://$WORKSPACE/securedlab -l $LAB_NAME -p $POD_NAME -s $DEPLOY_SCENARIO -i file://$WORKSPACE/opnfv.iso -H -B $BRIDGE -S $TMPDIR"

# log info to console
echo "Deployment parameters"
echo "--------------------------------------------------------"
echo "Scenario: $DEPLOY_SCENARIO"
echo "Lab: $LAB_NAME"
echo "POD: $POD_NAME"
echo "ISO: ${OPNFV_ARTIFACT_URL/*\/}"
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
