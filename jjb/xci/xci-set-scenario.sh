#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 SUSE and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o pipefail

#----------------------------------------------------------------------
# This script is used by CI and executed by Jenkins jobs.
# You are not supposed to use this script manually if you don't know
# what you are doing.
#----------------------------------------------------------------------

# This function allows developers to specify the impacted scenario by adding
# the info about installer and scenario into the commit message or using
# the topic branch names. This results in either skipping the real verification
# totally or skipping the determining the installer and scenario programmatically.
# It is important to note that this feature is only available to generic scenarios
# and only single installer/scenario pair is allowed.
# The input in commit message should be placed at the end of the commit message body,
# before the signed-off and change-id lines.
#
# Pattern to be searched in Commit Message
#   deploy-scenario:<scenario-name>
#   installer-type:<installer-type>
# Examples:
#   deploy-scenario:os-odl-nofeature
#   installer-type:osa
#
#   deploy-scenario:k8-nosdn-nofeature
#   installer-type:kubespray
#
# Patterns to be searched in topic branch name
#   skip-verify
#   skip-deployment
#   force-verify
function override_scenario() {
    echo "Processing $GERRIT_PROJECT patchset $GERRIT_REFSPEC"

    # ensure the metadata we record is consistent for all types of patches including skipped ones
    # extract releng-xci sha
    XCI_SHA=$(cd $WORKSPACE && git rev-parse HEAD)

    # extract scenario sha which is same as releng-xci sha for generic scenarios
    SCENARIO_SHA=$XCI_SHA

    # process topic branch names
    if [[ "$GERRIT_TOPIC" =~ skip-verify|skip-deployment|force-verify ]]; then
        [[ "$GERRIT_TOPIC" =~ force-verify ]] && echo "Forcing CI verification using default scenario and installer!"
        [[ "$GERRIT_TOPIC" =~ skip-verify|skip-deployment ]] && echo "Skipping verification!"
        echo "INSTALLER_TYPE=osa" > $WORK_DIRECTORY/scenario.properties
        echo "DEPLOY_SCENARIO=os-nosdn-nofeature" >> $WORK_DIRECTORY/scenario.properties
        echo "XCI_SHA=$XCI_SHA" >> $WORK_DIRECTORY/scenario.properties
        echo "SCENARIO_SHA=$SCENARIO_SHA" >> $WORK_DIRECTORY/scenario.properties
        echo "PROJECT_NAME=$GERRIT_PROJECT" >> $WORK_DIRECTORY/scenario.properties
        exit 0
    fi

    # process commit message
    if [[ "$GERRIT_CHANGE_COMMIT_MESSAGE" =~ "installer-type:" && "$GERRIT_CHANGE_COMMIT_MESSAGE" =~ "deploy-scenario:" ]]; then
        INSTALLER_TYPE=$(echo $GERRIT_CHANGE_COMMIT_MESSAGE | awk '/installer-type:/' RS=" " | cut -d":" -f2)
        DEPLOY_SCENARIO=$(echo $GERRIT_CHANGE_COMMIT_MESSAGE | awk '/deploy-scenario:/' RS=" " | cut -d":" -f2)

        if [[ -z "$INSTALLER_TYPE" || -z "$DEPLOY_SCENARIO" ]]; then
            echo "Installer type or deploy scenario is not specified. Falling back to programmatically determining them."
        else
            echo "Recording the installer '$INSTALLER_TYPE' and scenario '$DEPLOY_SCENARIO' for downstream jobs"
            echo "INSTALLER_TYPE=$INSTALLER_TYPE" > $WORK_DIRECTORY/scenario.properties
            echo "DEPLOY_SCENARIO=$DEPLOY_SCENARIO" >> $WORK_DIRECTORY/scenario.properties
            echo "XCI_SHA=$XCI_SHA" >> $WORK_DIRECTORY/scenario.properties
            echo "SCENARIO_SHA=$SCENARIO_SHA" >> $WORK_DIRECTORY/scenario.properties
            echo "PROJECT_NAME=$GERRIT_PROJECT" >> $WORK_DIRECTORY/scenario.properties
            exit 0
        fi
    else
        echo "Installer type or deploy scenario is not specified. Falling back to programmatically determining them."
    fi
}

# This function determines the impacted scenario by processing the Gerrit
# change and using diff to see what changed. If changed files belong to a scenario
# its name gets recorded for deploying and testing the right scenario.
#
# Pattern
#   <project-repo>/scenarios/<scenario>/<impacted files>: <scenario>
function determine_scenario() {
    echo "Processing $GERRIT_PROJECT patchset $GERRIT_REFSPEC"

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
    DEPLOY_SCENARIO+=$(git diff HEAD^..HEAD --name-only | grep scenarios | awk -F '[/|/]' '{print $2}' | uniq)

    # extract releng-xci sha
    XCI_SHA=$(cd $WORKSPACE && git rev-parse HEAD)

    # extract scenario sha
    SCENARIO_SHA=$(cd $WORK_DIRECTORY/$GERRIT_PROJECT && git rev-parse HEAD)
}

echo "Determining the impacted scenario"

declare -a DEPLOY_SCENARIO

# ensure GERRIT_TOPIC is set
GERRIT_TOPIC="${GERRIT_TOPIC:-''}"

# this directory is where the temporary clones and files are created
# while extracting the impacted scenario
WORK_DIRECTORY=/tmp/$GERRIT_CHANGE_NUMBER/$DISTRO
/bin/rm -rf $WORK_DIRECTORY && mkdir -p $WORK_DIRECTORY

if [[ $GERRIT_PROJECT == "releng-xci" ]]; then
    override_scenario
else
    determine_scenario
fi

# ensure single scenario is impacted
    if [[ $(IFS=$'\n' echo ${DEPLOY_SCENARIO[@]} | wc -w) != 1 ]]; then
    echo "Change impacts multiple scenarios!"
    echo "XCI doesn't support testing of changes that impact multiple scenarios currently."
    echo "Please split your change into multiple different/dependent changes, each modifying single scenario."
    exit 1
fi

# set the installer
case ${DEPLOY_SCENARIO[0]} in
    os-*)
        INSTALLER_TYPE=osa
        ;;
    k8-*)
        INSTALLER_TYPE=kubespray
        ;;
    *)
        echo "Unable to determine the installer. Exiting!"
        exit 1
        ;;
esac

# save the installer and scenario names into java properties file
# so they can be injected to downstream jobs via envInject
echo "Recording the installer '$INSTALLER_TYPE' and scenario '${DEPLOY_SCENARIO[0]}' and SHAs for downstream jobs"
echo "INSTALLER_TYPE=$INSTALLER_TYPE" > $WORK_DIRECTORY/scenario.properties
echo "DEPLOY_SCENARIO=$DEPLOY_SCENARIO" >> $WORK_DIRECTORY/scenario.properties
echo "XCI_SHA=$XCI_SHA" >> $WORK_DIRECTORY/scenario.properties
echo "SCENARIO_SHA=$SCENARIO_SHA" >> $WORK_DIRECTORY/scenario.properties
echo "PROJECT_NAME=$GERRIT_PROJECT" >> $WORK_DIRECTORY/scenario.properties

# skip scenario support check if the job is promotion job
if [[ "$JOB_NAME" =~ (os|k8) ]]; then
    exit 0
fi

# skip the deployment if the scenario is not supported on this distro
OPNFV_SCENARIO_REQUIREMENTS=$WORKSPACE/xci/opnfv-scenario-requirements.yml
if ! sed -n "/^- scenario: ${DEPLOY_SCENARIO[0]}$/,/^$/p" $OPNFV_SCENARIO_REQUIREMENTS | grep -q $DISTRO; then
    echo "# SKIPPED: Scenario ${DEPLOY_SCENARIO[0]} is NOT supported on $DISTRO"
    exit 0
fi
