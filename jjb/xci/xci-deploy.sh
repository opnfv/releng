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
sudo /bin/rm -rf /opt/openstack-ansible /opt/stack /opt/releng /opt/functest

# Fix up permissions
fix_ownership

# openstack-ansible enables strict host key checking by default
export ANSIBLE_HOST_KEY_CHECKING=False

# ensure the versions to checkout are set
export OPENSTACK_OSA_VERSION=${OPENSTACK_OSA_VERSION:-master}
export OPNFV_RELENG_VERSION=${OPNFV_RELENG_VERSION:-master}

# log some info
echo -e "\n"
echo "***********************************************************************"
echo "*                                                                     *"
echo "*                         Deploy OpenStack                            *"
echo "*                                                                     *"
echo "                 openstack-ansible version: $OPENSTACK_OSA_VERSION"
echo "                       releng version: $OPNFV_RELENG_VERSION"
echo "*                                                                     *"
echo "***********************************************************************"
echo -e "\n"
# clone releng repo
sudo git clone --quiet https://gerrit.opnfv.org/gerrit/releng /opt/releng
cd /opt/releng && sudo git checkout --quiet $OPNFV_RELENG_VERSION
echo "xci: using releng commit"
git show --oneline -s --pretty=format:'%h - %s (%cr) <%an>'

# display the nodes
echo "xci: OpenStack nodes"
cd /opt/bifrost
source env-vars
ironic node-list

# this script will be reused for promoting openstack-ansible versions and using
# promoted openstack-ansible versions as part of xci daily.
USE_PROMOTED_VERSIONS=${USE_PROMOTED_VERSIONS:-false}
if [ $USE_PROMOTED_VERSIONS = "true" ]; then
    echo "TBD: Will use the promoted versions of openstack/opnfv projects"
fi

cd /opt/releng/prototypes/openstack-ansible/scripts
sudo -E ./osa-deploy.sh

# log some info
echo -e "\n"
echo "***********************************************************************"
echo "*                                                                     *"
echo "*                OpenStack deployment is completed!                   *"
echo "*                                                                     *"
echo "***********************************************************************"
echo -e "\n"
