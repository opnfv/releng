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
        sudo chown -R jenkins:jenkins $WORKSPACE
        sudo chown -R jenkins:jenkins ${HOME}/.cache
    fi
}

# check distro to see if we support it
if [[ ! "$DISTRO" =~ (trusty|centos7|suse) ]]; then
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

# place bridge creation file on the right path
sudo mkdir -p /opt/puppet-infracloud/files/elements/infra-cloud-bridge/static/opt
sudo cp /opt/puppet-infracloud/templates/bifrost/create_bridge.py.erb /opt/puppet-infracloud/files/elements/infra-cloud-bridge/static/opt/create_bridge.py

# replace bridge name
sudo sed -i s/"<%= @bridge_name -%>"/br_opnfv/g /opt/puppet-infracloud/files/elements/infra-cloud-bridge/static/opt/create_bridge.py

# cleanup remnants of previous deployment
cd /opt/bifrost
sudo -E ./scripts/destroy-env.sh

# provision 3 VMs; jumphost, controller, and compute
cd /opt/bifrost
sudo -E ./scripts/test-bifrost-deployment.sh

# list the provisioned VMs
cd /opt/bifrost
source env-vars
ironic node-list
virsh list
