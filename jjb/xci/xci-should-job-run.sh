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
    echo "# SKIPPED: Patch doesn't impact deployment"
fi

# skip the deployment if the scenario is not supported on this distro
OPNFV_SCENARIO_REQUIREMENTS=$WORKSPACE/xci/opnfv-scenario-requirements.yml
if ! sed -n "/^- scenario: $DEPLOY_SCENARIO$/,/^- scenario/p" $OPNFV_SCENARIO_REQUIREMENTS | grep -q $DISTRO; then
    echo "# SKIPPED: Scenario $DEPLOY_SCENARIO is NOT supported on $DISTRO"
fi

sudo virsh destroy ${DISTRO}_xci_vm
sudo virsh undefine ${DISTRO}_xci_vm
exit 1
