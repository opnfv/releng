#!/bin/bash

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

sudo virsh destroy ${DISTRO}_xci_vm
sudo virsh undefine ${DISTRO}_xci_vm
