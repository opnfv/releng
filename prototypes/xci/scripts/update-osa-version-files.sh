#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2017 SUSE LINUX GmbH and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# This script is used to pin the SHAs for the various roles in the
# ansible-role-requirements file. It will also update the SHAs for
# OSA and bifrost.

set -e

# NOTE(hwoarang) This could break if files are re-arranged in the future
releng_xci_base="$(dirname $(readlink -f $0))/.."

usage() {
    echo """
    ${0} <openstack-ansible commit SHA> [<bifrost commit SHA>]
    """
    exit 0
}

cleanup() {
    [[ -d $tempdir ]] && rm -rf $tempdir
}

printme() {
    echo "===> $1"
}

# Only need a single argument
[[ $# -lt 1 || $# -gt 2 ]] && echo "Invalid number of arguments!" && usage

tempdir="$(mktemp -d)"

trap cleanup EXIT

pushd $tempdir &> /dev/null

printme "Downloading the sources-branch-updater-lib.sh library"

printme "Cloning the openstack-ansible repository"
(
    git clone -q git://git.openstack.org/openstack/openstack-ansible && cd openstack-ansible && git checkout -q $1
)

popd &> /dev/null

pushd $tempdir/openstack-ansible &> /dev/null
source scripts/sources-branch-updater-lib.sh
printme "Synchronize roles and packages"
update_ansible_role_requirements "master" "true" "true"

# Construct the ansible-role-requirements-file
echo """---
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2017 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
# these versions are extracted based on the osa commit ${1} on $(git --no-pager log -1 --format=%cI $1)
# https://review.openstack.org/gitweb?p=openstack/openstack-ansible.git;a=commit;h=$1""" > $releng_xci_base/file/ansible-role-requirements.yml
cat $tempdir/openstack-ansible/ansible-role-requirements.yml >> $releng_xci_base/file/ansible-role-requirements.yml

# Update the pinned OSA version
sed -i -e "/^export OPENSTACK_OSA_VERSION/s@:-\"[a-z0-9]*@:-\"${1}@" \
    -e "s/\(^# HEAD of osa.*of \).*/\1$(date +%d\.%m\.%Y)/" $releng_xci_base/config/pinned-versions

# Update the pinned bifrost version
[[ -n ${2:-} ]] && \
    sed -i -e "/^export OPENSTACK_BIFROST_VERSION/s@:-\"[a-z0-9]*@:-\"${2}@" \
    -e "s/\(^# HEAD of bifrost.*of \).*/\1$(date +%d\.%m\.%Y)/" $releng_xci_base/config/pinned-versions

popd &> /dev/null

printme ""
printme "======================= Report ============================"
printme ""
printme "The $releng_xci_base/file/ansible-role-requirements.yml and"
printme "$releng_xci_base/config/pinned-versions files have been"
printme "updated. Please make sure you test the end result before"
printme "committing it!"
printme ""
printme "==========================================================="
