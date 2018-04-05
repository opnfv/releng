#!/bin/bash
set -o nounset
set -o pipefail

echo "--------------------------------------------------------"
echo "This is $INSTALLER_TYPE deploy job!"
echo "--------------------------------------------------------"

DEPLOY_SCENARIO=${DEPLOY_SCENARIO:-"os-nosdn-nofeature-noha"}
BRIDGE=${BRIDGE:-pxebr}
LAB_NAME=${NODE_NAME/-*}
POD_NAME=${NODE_NAME/*-}
deploy_ret=0

if [[ ! "$NODE_NAME" =~ "-virtual" ]] && [[ ! "$LAB_NAME" =~ (zte) ]]; then
    echo "Unsupported lab $LAB_NAME for now, Cannot continue!"
    exit $deploy_ret
fi

# clone the securedlab/pharos repo
cd $WORKSPACE

# There are no PDFs in euphrates branch of pharos repo.
if [[  "$BRANCH" =~ "euphrates" ]]; then
    CONFIG_REPO_NAME=securedlab
else
    CONFIG_REPO_NAME=pharos
fi

if [[  "$BRANCH" =~ "master" ]]; then
    DOCTOR_OPT="-d 1"
else
    DOCTOR_OPT=""
fi

LABS_DIR=/var/tmp/opnfv-${CONFIG_REPO_NAME}

echo "Cloning ${CONFIG_REPO_NAME} repo $BRANCH to $LABS_DIR"
sudo rm -rf $LABS_DIR
git clone ssh://jenkins-zte@gerrit.opnfv.org:29418/${CONFIG_REPO_NAME} \
    --quiet --branch $BRANCH $LABS_DIR

DEPLOY_COMMAND="sudo -E ./ci/deploy/deploy.sh -L $LABS_DIR \
                -l $LAB_NAME -p $POD_NAME -B $BRIDGE -s $DEPLOY_SCENARIO \
                $DOCTOR_OPT"

# log info to console
echo """
Deployment parameters
--------------------------------------------------------
Scenario: $DEPLOY_SCENARIO
LAB: $LAB_NAME
POD: $POD_NAME
BRIDGE: $BRIDGE

Starting the deployment using $INSTALLER_TYPE. This could take some time...
--------------------------------------------------------
Issuing command
$DEPLOY_COMMAND
"""

# start the deployment
$DEPLOY_COMMAND

if [ $? -ne 0 ]; then
    echo
    echo "Depolyment failed!"
    deploy_ret=1
else
    echo
    echo "--------------------------------------------------------"
    echo "Deployment done!"
fi

exit $deploy_ret
