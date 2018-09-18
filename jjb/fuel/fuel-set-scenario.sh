#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 SUSE, Mirantis Inc., Enea Software AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o pipefail
set -x

#----------------------------------------------------------------------
# This script is used by CI and executed by Jenkins jobs.
# You are not supposed to use this script manually if you don't know
# what you are doing.
#----------------------------------------------------------------------

# This function allows developers to specify the impacted scenario by 
# requesting a RE-check via a gerrit change comment under a specific format.
#
# Patterns to be searched in change comment
#   recheck: <scenario-name>
#   reverify: <scenario-name>
# Examples:
#   recheck: os-odl-ovs-noha
#   reverify: os-nosdn-nofeature-ha

function set_scenario() {
    # process gerrit event comment text (if present), topic branch name
    DEPLOY_SCENARIO=$(echo "${GERRIT_EVENT_COMMENT_TEXT}" | \
                      grep -Po '(?!:(recheck|reverify):\s*)([-\w]+ha)')
    if [ -z "${DEPLOY_SCENARIO}" ]; then
        if [[ "$GERRIT_TOPIC" =~ baremetal ]]; then
            DEPLOY_SCENARIO='os-nosdn-nofeature-ha'
        else
            DEPLOY_SCENARIO='os-nosdn-nofeature-noha'
        fi
    fi
    # save the scenario names into java properties file
    # so they can be injected to downstream jobs via envInject
    echo "Recording the scenario '${DEPLOY_SCENARIO}' for downstream jobs"
    echo "DEPLOY_SCENARIO=${DEPLOY_SCENARIO}" >> $WORK_DIRECTORY/scenario.properties
}

# ensure GERRIT vars are set
[ -n "${GERRIT_CHANGE_NUMBER}" ] || exit 1
GERRIT_TOPIC="${GERRIT_TOPIC:-''}"
GERRIT_EVENT_COMMENT_TEXT="${GERRIT_EVENT_COMMENT_TEXT:-''}"

# this directory is where the temporary properties file will be stored
WORK_DIRECTORY=/tmp/$GERRIT_CHANGE_NUMBER
/bin/rm -rf $WORK_DIRECTORY && mkdir -p $WORK_DIRECTORY

set_scenario
