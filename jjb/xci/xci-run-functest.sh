#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 SUSE and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o nounset

#----------------------------------------------------------------------
# This script is used by CI and executed by Jenkins jobs.
# You are not supposed to use this script manually if you don't know
# what you are doing.
#----------------------------------------------------------------------

# ensure GERRIT_TOPIC is set
GERRIT_TOPIC="${GERRIT_TOPIC:-''}"

# skip the healthcheck if the patch doesn't impact the deployment
if [[ "$GERRIT_TOPIC" =~ skip-verify|skip-deployment ]]; then
    echo "Skipping the healthcheck!"
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

# skip the deployment if the scenario is not supported on this distro
OPNFV_SCENARIO_REQUIREMENTS=$WORKSPACE/xci/opnfv-scenario-requirements.yml
if ! sed -n "/^- scenario: $DEPLOY_SCENARIO$/,/^$/p" $OPNFV_SCENARIO_REQUIREMENTS | grep -q $DISTRO; then
    echo "# SKIPPED: Scenario $DEPLOY_SCENARIO is NOT supported on $DISTRO"
    exit 0
fi

# set XCI_VENV for ansible
export XCI_PATH=/home/devuser/releng-xci
export XCI_VENV=${XCI_PATH}/venv

ssh -F $HOME/.ssh/${DISTRO}-xci-vm-config ${DISTRO}_xci_vm "source $XCI_VENV/bin/activate; while read var; do declare -x \"\${var}\" 2>/dev/null; done < ${XCI_PATH}/.cache/xci.env && cd releng-xci/xci && ansible-playbook -i xci/playbook/dynamic_inventory.py playbooks/prepare-functest.yml"
echo "Running functest"
ssh -F $HOME/.ssh/${DISTRO}-xci-vm-config ${DISTRO}_xci_vm_opnfv "/root/run-functest.sh"
# Record exit code
functest_exit=$?

case ${DEPLOY_SCENARIO[0]} in
    os-*)
        FUNCTEST_LOG=/root/results/functest.log
        ;;
    k8-*)
        FUNCTEST_LOG=/root/results/functest-kubernetes.log
        ;;
    *)
        echo "Unable to determine the installer. Exiting!"
        exit 1
        ;;
esac

echo "Functest log"
echo "---------------------------------------------------------------------------------"
ssh -F $HOME/.ssh/${DISTRO}-xci-vm-config ${DISTRO}_xci_vm_opnfv "cat $FUNCTEST_LOG"
echo "---------------------------------------------------------------------------------"
exit ${functest_exit}
