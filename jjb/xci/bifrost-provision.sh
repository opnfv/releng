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
sudo /bin/rm -rf /opt/bifrost /opt/openstack-ansible /opt/releng /opt/functest

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

# source flavor vars
source "$WORKSPACE/prototypes/xci/config/${XCI_FLAVOR}-vars"

# combine opnfv and upstream scripts/playbooks
sudo /bin/cp -rf /opt/releng/prototypes/bifrost/* /opt/bifrost/

# cleanup remnants of previous deployment
cd /opt/bifrost
sudo -E ./scripts/destroy-env.sh

# provision VMs for the flavor
cd /opt/bifrost
./scripts/bifrost-provision.sh

# list the provisioned VMs
cd /opt/bifrost
source env-vars
ironic node-list
sudo -H -E virsh list

echo "OpenStack nodes are provisioned!"
# here we have to do something in order to capture what was the working sha1
# hardcoding stuff for the timebeing

cd /opt/bifrost
BIFROST_GIT_SHA1=$(git rev-parse HEAD)

# log some info
echo -e "\n"
echo "***********************************************************************"
echo "*                       BIFROST SHA1 TO PIN                           *"
echo "*                                                                     *"
echo "    $BIFROST_GIT_SHA1"
echo "*                                                                     *"
echo "***********************************************************************"

echo -e "\n"
