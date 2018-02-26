#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 SUSE and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

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

WORK_DIRECTORY=/tmp/$GERRIT_CHANGE_NUMBER/$DISTRO
/bin/rm -rf $WORK_DIRECTORY && mkdir -p $WORK_DIRECTORY

# if change is coming to releng-xci, continue as usual until that part is fixed as well
if [[ $GERRIT_PROJECT == "releng-xci" ]]; then
    # save the scenario name into java properties file to be injected to downstream jobs via envInject
    echo "Recording scenario name for downstream jobs"
    echo "DEPLOY_SCENARIO=os-nosdn-nofeature" > $WORK_DIRECTORY/scenario.properties
    exit 0
fi

# projects develop different scenarios and jobs need to know which scenario got the
# change under test so the jobs can deploy and test the right scenario.
# we need to fetch the change and look at the changeset to find out the scenario instead
# of hardcoding scenario per project.

git clone https://gerrit.opnfv.org/gerrit/$GERRIT_PROJECT $WORK_DIRECTORY/$GERRIT_PROJECT
cd $WORK_DIRECTORY/$GERRIT_PROJECT
git fetch https://gerrit.opnfv.org/gerrit/$GERRIT_PROJECT $GERRIT_REFSPEC && git checkout FETCH_HEAD
DEPLOY_SCENARIO=$(git diff HEAD^..HEAD --name-only | grep scenarios | sed -r 's/scenarios\/(.*?)\/role.*/\1/' | uniq)

# ensure single scenario is impacted
if [[ $(echo $DEPLOY_SCENARIO | wc -w) != 1 ]]; then
    echo "Change impacts multiple scenarios!"
    echo "XCI doesn't support testing of changes that impact multiple scenarios currently."
    echo "Please split your change into multiple different/dependent changes, each modifying single scenario."
    exit 1
fi

# save the scenario name into java properties file to be injected to downstream jobs via envInject
echo "Recording scenario name for downstream jobs"
echo "DEPLOY_SCENARIO=$DEPLOY_SCENARIO" > $WORK_DIRECTORY/scenario.properties

# skip the deployment if the scenario is not supported on this distro
OPNFV_SCENARIO_REQUIREMENTS=$WORKSPACE/xci/opnfv-scenario-requirements.yml
if ! sed -n "/^- scenario: $DEPLOY_SCENARIO$/,/^$/p" $OPNFV_SCENARIO_REQUIREMENTS | grep -q $DISTRO; then
    echo "# SKIPPED: Scenario $DEPLOY_SCENARIO is NOT supported on $DISTRO"
    exit 0
fi
