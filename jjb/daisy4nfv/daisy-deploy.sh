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

# clone the securedlab repo
cd $WORKSPACE
BASE_DIR=$(cd ./;pwd)
SECURELAB_DIR=/var/tmp/opnfv-securedlab

echo "Cloning securedlab repo $BRANCH to $SECURELAB_DIR"
rm -rf $SECURELAB_DIR
git clone ssh://jenkins-zte@gerrit.opnfv.org:29418/securedlab --quiet \
    --branch $BRANCH $SECURELAB_DIR

DEPLOY_COMMAND="sudo -E ./ci/deploy/deploy.sh -b $BASE_DIR -L $SECURELAB_DIR \
                -l $LAB_NAME -p $POD_NAME -B $BRIDGE -s $DEPLOY_SCENARIO"

# log info to console
echo """
Deployment parameters
--------------------------------------------------------
Scenario: $DEPLOY_SCENARIO
LAB: $LAB_NAME
POD: $POD_NAME
BRIDGE: $BRIDGE
BASE_DIR: $BASE_DIR

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
