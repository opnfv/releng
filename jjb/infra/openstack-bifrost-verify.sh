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

# check distro to see if we support it
# we will have centos and suse supported in future
case "$DISTRO" in
    trusty)
        #start the test
        echo "Starting provisioning of 3 VMs"
        ;;
    *)
        echo "Distro $DISTRO is not supported!"
        exit 1
esac

# remove previously cloned repos
/bin/rm -rf /opt/bifrost /opt/puppet-infracloud /opt/stack /opt/releng

# clone upstream bifrost repo and checkout the patch to verify
git clone https://git.openstack.org/openstack/bifrost /opt/bifrost
cd /opt/bifrost
git fetch https://git.openstack.org/openstack/bifrost $GERRIT_REFSPEC && git checkout FETCH_HEAD

# clone puppet-infracloud
git clone https://git.openstack.org/openstack-infra/puppet-infracloud /opt/puppet-infracloud

# combine opnfv and upstream scripts/playbooks
cp -R $WORKSPACE/prototypes/bifrost/* /opt/bifrost/

# cleanup remnants of previous deployment
cd /opt/bifrost
./scripts/destroy-env.sh

# provision 3 VMs; jumphost, controller, and compute
cd /opt/bifrost
./scripts/test-bifrost-deployment.sh

# list the provisioned VMs
cd /opt/bifrost
source env-vars
ironic node-list
virsh list
