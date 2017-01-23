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

trap fix_ownership EXIT

function fix_ownership() {
    if [ -z "${JOB_URL+x}" ]; then
        echo "Not running as part of Jenkins. Handle the logs manually."
    else
        # Make sure cache exists
        [[ ! -d ${HOME}/.cache ]] && mkdir ${HOME}/.cache

        sudo chown -R jenkins:jenkins $WORKSPACE
        sudo chown -R jenkins:jenkins ${HOME}/.cache
    fi
}

# check distro to see if we support it
if [[ ! "$DISTRO" =~ (xenial) ]]; then
    echo "Distro $DISTRO is not supported!"
    exit 1
fi

# remove previously cloned repos
sudo /bin/rm -rf /opt/bifrost /opt/puppet-infracloud /opt/stack /opt/releng

# Fix up permissions
fix_ownership

# clone all the repos first and checkout the patch afterwards
sudo git clone https://git.openstack.org/openstack/bifrost /opt/bifrost
sudo git clone https://git.openstack.org/openstack-infra/puppet-infracloud /opt/puppet-infracloud
sudo git clone https://gerrit.opnfv.org/gerrit/releng /opt/releng

# checkout the patch
cd $CLONE_LOCATION
sudo git fetch $PROJECT_REPO $GERRIT_REFSPEC && sudo git checkout FETCH_HEAD

# combine opnfv and upstream scripts/playbooks
sudo /bin/cp -rf /opt/releng/prototypes/bifrost/* /opt/bifrost/

# cleanup remnants of previous deployment
cd /opt/bifrost
sudo -E ./scripts/destroy-osa-env.sh

# provision 6 VMs; jumphost, controllers, and computes
cd /opt/bifrost
sudo -E ./scripts/test-bifrost-osa-deployment.sh

# list the provisioned VMs
cd /opt/bifrost
source env-vars
ironic node-list
virsh list

# deploy openstack
cd /opt/releng/prototypes/openstack-ansible/scripts
sudo -E ./osa_deploy.sh
