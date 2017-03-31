#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

cd $WORKSPACE/prototypes/xci

# for daily jobs, we want to use working versions
# for periodic jobs, we will use whatever is set in the job, probably master
if [[ "$JOB_NAME" =~ "daily" ]]; then
    # source pinned-vars to get releng version
    source ./config/pinned-versions

    # checkout the version
    git checkout -q $OPNFV_RELENG_VERSION
    echo "Info: Using $OPNFV_RELENG_VERSION"
elif [[ "$JOB_NAME" =~ "periodic" ]]; then
    echo "Info: Using $OPNFV_RELENG_VERSION"
fi

# this is just an example to give the idea about what we need to do
# so ignore this part for the timebeing as we need to adjust xci-deploy.sh
# to take this into account while deploying anyways
# clone openstack-ansible
if [[ "$JOB_NAME" =~ "periodic" ]]; then
    cd $WORKSPACE
    echo "Info: Capture the ansible role requirement versions before doing anything"
    git clone -q https://review.openstack.org/p/openstack/openstack-ansible.git
    cd openstack-ansible
    cat ansible-role-requirements.yml | while IFS= read -r line
    do
        if [[ $line =~ "src:" ]]; then
            repo_url=$(echo $line | awk {'print $2'})
            repo_sha1=$(git ls-remote $repo_url $git_branch | awk {'print $1'})
        fi
        echo "$line" | sed -e "s|master|$repo_sha1|" >> opnfv-ansible-role-requirements.yml
    done
    echo "Info: SHA1s of ansible role requirements"
    echo "-------------------------------------------------------------------------"
    cat opnfv-ansible-role-requirements.yml
    echo "-------------------------------------------------------------------------"
fi

# proceed with the deployment
cd $WORKSPACE/prototypes/xci
sudo -E ./xci-deploy.sh
