#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 SUSE and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

#----------------------------------------------------------------------
# This script is used by CI and executed by Jenkins jobs.
# You are not supposed to use this script manually if you don't know
# what you are doing.
#----------------------------------------------------------------------

# skip the deployment if the patch doesn't impact the deployment
if [[ "$GERRIT_TOPIC" =~ 'skip-verify' ]]; then
    echo "Skipping the deployment!"
    exit 0
fi

# if the scenario is external, we need to wipe WORKSPACE to place releng-xci there since
# the project where the scenario is coming from is cloned and the patch checked out to the
# xci/scenarios/$DEPLOY_SCENARIO to be synched on clean VM
# apart from that, we need releng-xci stuff in WORKSPACE for things to function correctly on Jenkins.
# if the change is coming to releng-xci, we don't need to do anything since the patch is checked
# out to the WORKSPACE anyways
if [[ $GERRIT_PROJECT != "releng-xci" ]]; then
    /bin/rm -rf $WORKSPACE
    git clone https://gerrit.opnfv.org/gerrit/releng-xci $WORKSPACE
fi

# skip the deployment if the scenario is not supported on this distro
OPNFV_SCENARIO_REQUIREMENTS=$WORKSPACE/xci/opnfv-scenario-requirements.yml
if ! sed -n "/^- scenario: $DEPLOY_SCENARIO$/,/^$/p" $OPNFV_SCENARIO_REQUIREMENTS | grep -q $DISTRO; then
    echo "# SKIPPED: Scenario $DEPLOY_SCENARIO is NOT supported on $DISTRO"
    exit 0
fi

cd $WORKSPACE

# The start-new-vm.sh script will copy the entire releng-xci directory
# so lets prepare the test script now so it can be copied by the script.
# Please do not move it elsewhere or you would have to move it to the VM
# yourself.
cat > xci_test.sh<<EOF
#!/bin/bash
set -o pipefail
export DISTRO=$DISTRO
export DEPLOY_SCENARIO=$DEPLOY_SCENARIO
export FUNCTEST_MODE=$FUNCTEST_MODE
export FUNCTEST_SUITE_NAME=$FUNCTEST_SUITE_NAME
export XCI_FLAVOR=$XCI_FLAVOR
export CLEAN_DIB_IMAGES=$CLEAN_DIB_IMAGES
export OPNFV_RELENG_DEV_PATH=/home/devuser/releng-xci/
export INSTALLER_TYPE=$INSTALLER_TYPE
export GIT_BASE=$GIT_BASE
export JENKINS_HOME=$JENKINS_HOME

if [[ ! -z ${WORKSPACE+x} && $GERRIT_PROJECT != "releng-xci" ]]; then
    git clone https://gerrit.opnfv.org/gerrit/$GERRIT_PROJECT xci/scenarios/$DEPLOY_SCENARIO && cd xci/scenarios/$DEPLOY_SCENARIO
    git fetch https://gerrit.opnfv.org/gerrit/$GERRIT_PROJECT $GERRIT_REFSPEC && git checkout FETCH_HEAD
    cd -
fi

cd xci
./xci-deploy.sh | ts
EOF
chmod a+x xci_test.sh

export XCI_BUILD_CLEAN_VM_OS=false
export XCI_UPDATE_CLEAN_VM_OS=true

./xci/scripts/vm/start-new-vm.sh $DISTRO
