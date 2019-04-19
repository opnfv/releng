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

# ensure GERRIT_TOPIC is set
GERRIT_TOPIC="${GERRIT_TOPIC:-''}"

# skip the deployment if the patch doesn't impact the deployment
if [[ "$GERRIT_TOPIC" =~ skip-verify|skip-deployment ]]; then
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
    cd $HOME && /bin/rm -rf $WORKSPACE
    git clone https://gerrit.opnfv.org/gerrit/releng-xci $WORKSPACE && cd $WORKSPACE
    chmod -R go-rwx $WORKSPACE/xci/scripts/vm
fi

# skip the deployment if the scenario is not supported on this distro and installer combination
OPNFV_SCENARIO_REQUIREMENTS=$WORKSPACE/xci/opnfv-scenario-requirements.yml
if ! sed -n "/^- scenario: $DEPLOY_SCENARIO$/,/^$/p" $OPNFV_SCENARIO_REQUIREMENTS | \
     sed -n "/- installer: $INSTALLER_TYPE$/,/^$/p" | \
     grep -q $DISTRO; then
    echo "# SKIPPED: Scenario $DEPLOY_SCENARIO is NOT supported on $DISTRO and $INSTALLER_TYPE installer"
    exit 0
fi

ssh -F $HOME/.ssh/${DISTRO}-xci-vm-config ${DISTRO}_xci_vm "cd releng-xci && ./xci_test.sh"
