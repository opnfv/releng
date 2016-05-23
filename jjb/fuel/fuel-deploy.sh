#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
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

if [[ "$NODE_NAME" =~ "virtual" ]]; then
    POD_NAME="virtual_kvm"
fi

# we currently support ericsson, intel, lf and zte labs
if [[ ! "$LAB_NAME" =~ (ericsson|intel|lf|zte) ]]; then
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
echo "Deployment is done successfully!"

# Quick and dirty fix for SFC scenatio - will be fixed properly post-release
if [[ ! "$DEPLOY_SCENARIO" =~ "os-odl_l2-sfc" ]]; then
    exit 0
fi

echo
echo "SFC Scenario is deployed"
echo

# The stuff below is here temporarily and will be fixed once the release is out
# The stuff below is here temporarily and will be fixed once the release is out
export FUEL_MASTER_IP=10.20.0.2
export TACKER_SCRIPT_URL="https://git.opnfv.org/cgit/fuel/plain/prototypes/sfc_tacker/poc.tacker-up.sh?h=${GIT_BRANCH#*/}"
export CONTROLLER_NODE_IP=$(sshpass -pr00tme /usr/bin/ssh -o UserKnownHostsFile=/dev/null \
    -o StrictHostKeyChecking=no root@$FUEL_MASTER_IP 'fuel node list' | \
    grep opendaylight | cut -d'|' -f5)

# we can't do much if we do not have the controller IP
if [[ ! "$CONTROLLER_NODE_IP" =~ "10.20.0" ]]; then
    echo "Unable to retrieve controller IP"
    exit 1
fi

echo
echo "Copying and executing poc.tacker-up.sh script on controller node $CONTROLLER_NODE_IP"
echo

expect << END
spawn /usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -l root $::env(FUEL_MASTER_IP)
expect {
  -re ".*sword.*" {
    exp_send "r00tme\r"
  }
}
expect "# "
send "/usr/bin/ssh -l root $::env(CONTROLLER_NODE_IP)\r"
expect "# "
send "sudo apt-get install -y git\r"
expect "# "
send "/bin/mkdir -p /root/sfc-poc && cd /root/sfc-poc\r"
expect "# "
send "git clone https://gerrit.opnfv.org/gerrit/fuel && cd fuel\r"
expect "# "
send "git fetch https://gerrit.opnfv.org/gerrit/fuel refs/changes/97/10597/2 && git checkout FETCH_HEAD\r"
expect "# "
send "/bin/bash /root/sfc-poc/fuel/prototypes/sfc_tacker/poc.tacker-up.sh\r"
expect "# "
send "exit\r"
expect "Connection to $::env(CONTROLLER_NODE_IP) closed. "
send "exit\r"
expect "Connection to $::env(FUEL_MASTER_IP) closed. "
END
