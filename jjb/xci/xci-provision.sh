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

trap cleanup_and_upload EXIT

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

function cleanup_and_upload() {
    original_exit=$?
    fix_ownership
    exit $original_exit
}

# check distro to see if we support it
if [[ ! "$DISTRO" =~ (xenial|centos7|suse) ]]; then
    echo "Distro $DISTRO is not supported!"
    exit 1
fi

# remove previously cloned repos
sudo /bin/rm -rf /opt/bifrost /opt/openstack-ansible /opt/stack /opt/releng /opt/functest

# Fix up permissions
fix_ownership

# ensure the versions to checkout are set
export OPENSTACK_BIFROST_VERSION=${OPENSTACK_BIFROST_VERSION:-master}
export OPNFV_RELENG_VERSION=${OPNFV_RELENG_VERSION:-master}

# log some info
echo -e "\n"
echo "***********************************************************************"
echo "*                                                                     *"
echo "*                      Provision OpenStack Nodes                      *"
echo "*                                                                     *"
echo "                       bifrost version: $OPENSTACK_BIFROST_VERSION"
echo "                       releng version: $OPNFV_RELENG_VERSION"
echo "*                                                                     *"
echo "***********************************************************************"
echo -e "\n"

# clone the repos and checkout the versions
sudo git clone --quiet https://git.openstack.org/openstack/bifrost /opt/bifrost
cd /opt/bifrost && sudo git checkout --quiet $OPENSTACK_BIFROST_VERSION
echo "xci: using bifrost commit"
git show --oneline -s --pretty=format:'%h - %s (%cr) <%an>'

sudo git clone --quiet https://gerrit.opnfv.org/gerrit/releng /opt/releng
cd /opt/releng && sudo git checkout --quiet $OPNFV_RELENG_VERSION
echo "xci: using releng commit"
git show --oneline -s --pretty=format:'%h - %s (%cr) <%an>'

# this script will be reused for promoting bifrost versions and using
# promoted bifrost versions as part of xci daily.
USE_PROMOTED_VERSIONS=${USE_PROMOTED_VERSIONS:-false}
if [ $USE_PROMOTED_VERSIONS = "true" ]; then
    echo "TBD: Will use the promoted versions of openstack/opnfv projects"
fi

# combine opnfv and upstream scripts/playbooks
sudo /bin/cp -rf /opt/releng/prototypes/bifrost/* /opt/bifrost/

# cleanup remnants of previous deployment
cd /opt/bifrost
sudo -E ./scripts/destroy-env.sh

# provision 6 VMs; xcimaster, controller00, controller01, controller02, compute00, and compute01
cd /opt/bifrost
sudo -E ./scripts/osa-bifrost-deployment.sh

# list the provisioned VMs
cd /opt/bifrost
source env-vars
ironic node-list
virsh list

# log some info
echo -e "\n"
echo "***********************************************************************"
echo "*                                                                     *"
echo "*                 OpenStack nodes are provisioned!                    *"
echo "*                                                                     *"
echo "***********************************************************************"
echo -e "\n"
