#!/bin/bash

#----------------------------------------------------------------------
# This script is used by CI and executed by Jenkins jobs.
# You are not supposed to use this script manually if you don't know
# what you are doing.
#----------------------------------------------------------------------

# skip the healthcheck if the patch doesn't impact the deployment
if [[ "$GERRIT_TOPIC" =~ skip-verify|skip-deployment ]]; then
    echo "Skipping the healthcheck!"
    exit 0
fi

echo "Hello World!"
