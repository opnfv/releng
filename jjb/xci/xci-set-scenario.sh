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

# This function will determine the impacted generic scenario by processing the
# change and using diff to see what changed.
# It currently sets the scenario to os-nosdn-nofeature.
function determine_generic_scenario() {
    echo "Processing $GERRIT_PROJECT $GERRIT_REFSPEC"

    # set the default scenario
    DEPLOY_SCENARIO="os-nosdn-nofeature"
}

# This function determines the impacted external scenario by processing the Gerrit
# change and using diff to see what changed. If changed files belong to a scenario
# its name gets recorded for deploying and testing the right scenario.
#
# Pattern
# <project-repo>/scenarios/<scenario>/<impacted files>: <scenario>
function determine_external_scenario() {
    echo "Processing $GERRIT_PROJECT $GERRIT_REFSPEC"

    # remove the clone that is done via jenkins and place releng-xci there so the
    # things continue functioning properly
    cd $HOME && /bin/rm -rf $WORKSPACE
    git clone -q https://gerrit.opnfv.org/gerrit/releng-xci $WORKSPACE && cd $WORKSPACE

    # fix the permissions so ssh doesn't complain due to having world-readable keyfiles
    chmod -R go-rwx $WORKSPACE/xci/scripts/vm

    # clone the project repo and fetch the patchset to process for further processing
    git clone -q https://gerrit.opnfv.org/gerrit/$GERRIT_PROJECT $WORK_DIRECTORY/$GERRIT_PROJECT
    cd $WORK_DIRECTORY/$GERRIT_PROJECT
    git fetch -q https://gerrit.opnfv.org/gerrit/$GERRIT_PROJECT $GERRIT_REFSPEC && git checkout -q FETCH_HEAD

    # process the diff to find out what scenario(s) are impacted - there should only be 1
    DEPLOY_SCENARIO=$(git diff HEAD^..HEAD --name-only | grep scenarios | awk -F '[/|/]' '{print $2}' | uniq)
}

echo "Determining the impacted scenario"

# ensure GERRIT_TOPIC is set
GERRIT_TOPIC="${GERRIT_TOPIC:-''}"

# this directory is where the temporary clones and files are created
# while extracting the impacted scenario
WORK_DIRECTORY=/tmp/$GERRIT_CHANGE_NUMBER/$DISTRO
/bin/rm -rf $WORK_DIRECTORY && mkdir -p $WORK_DIRECTORY

# skip the healthcheck if the patch doesn't impact the deployment
if [[ "$GERRIT_TOPIC" =~ skip-verify|skip-deployment ]]; then
    echo "Skipping verify!"
    echo "DEPLOY_SCENARIO=os-nosdn-nofeature" > $WORK_DIRECTORY/scenario.properties
    exit 0
fi

if [[ $GERRIT_PROJECT == "releng-xci" ]]; then
    determine_generic_scenario
else
    determine_external_scenario
fi

# ensure single scenario is impacted
if [[ $(echo $DEPLOY_SCENARIO | wc -w) != 1 ]]; then
    echo "Change impacts multiple scenarios!"
    echo "XCI doesn't support testing of changes that impact multiple scenarios currently."
    echo "Please split your change into multiple different/dependent changes, each modifying single scenario."
    exit 1
fi

# set the installer
if [[ $DEPLOY_SCENARIO =~ ^(os-) ]]; then
    XCI_INSTALLER=osa
elif [[ $DEPLOY_SCENARIO =~ ^(k8-) ]]; then
    XCI_INSTALLER=kubespray
else
    echo "Unable to determine the installer. Exiting!"
    exit 1
fi

# save the installer and scenario names into java properties file
# so they can be injected to downstream jobs via envInject
echo "Recording the installer '$XCI_INSTALLER' and scenario '$DEPLOY_SCENARIO' for downstream jobs"
echo "XCI_INSTALLER=$XCI_INSTALLER" > $WORK_DIRECTORY/scenario.properties
echo "DEPLOY_SCENARIO=$DEPLOY_SCENARIO" >> $WORK_DIRECTORY/scenario.properties

# skip the deployment if the scenario is not supported on this distro
OPNFV_SCENARIO_REQUIREMENTS=$WORKSPACE/xci/opnfv-scenario-requirements.yml
if ! sed -n "/^- scenario: $DEPLOY_SCENARIO$/,/^$/p" $OPNFV_SCENARIO_REQUIREMENTS | grep -q $DISTRO; then
    echo "# SKIPPED: Scenario $DEPLOY_SCENARIO is NOT supported on $DISTRO"
    exit 0
fi
