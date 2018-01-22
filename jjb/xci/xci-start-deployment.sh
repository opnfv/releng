#!/bin/bash

#----------------------------------------------------------------------
# This script is used by CI and executed by Jenkins jobs.
# You are not supposed to use this script manually if you don't know
# what you are doing.
#----------------------------------------------------------------------

# skip the deployment if the patch doesn't impact the deployment
if [[ "$GERRIT_TOPIC" =~ skip-verify|skip-deployment ]]; then
    echo "Skipping the deployment!"
    exit 0
fi

ssh -F $HOME/.ssh/xci-vm-config ${DISTRO}_xci_vm "cd releng-xci && ./xci_test.sh"
