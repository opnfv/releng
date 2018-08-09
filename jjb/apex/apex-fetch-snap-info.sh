#!/usr/bin/env bash

##############################################################################
# Copyright (c) 2018 Tim Rozet (Red Hat) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

set -o errexit
set -o nounset
set -o pipefail

echo "Fetching overcloudrc, ssh key, and node.yaml from deployment..."

SSH_OPTIONS=(-o StrictHostKeyChecking=no -o GlobalKnownHostsFile=/dev/null -o UserKnownHostsFile=/dev/null -o LogLevel=error)

tmp_dir=/tmp/csit
rm -rf ${tmp_dir}
mkdir -p ${tmp_dir}

# TODO(trozet) remove this after fix goes in for tripleo_inspector to copy these
pushd ${tmp_dir} > /dev/null
echo "Copying overcloudrc and ssh key from Undercloud..."
# Store overcloudrc
UNDERCLOUD=$(sudo virsh domifaddr undercloud | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
sudo scp ${SSH_OPTIONS[@]} stack@${UNDERCLOUD}:overcloudrc ./
# Copy out ssh key of stack from undercloud
sudo scp ${SSH_OPTIONS[@]} stack@${UNDERCLOUD}:.ssh/id_rsa ./
sudo chmod 0600 id_rsa
popd > /dev/null

echo "Gathering introspection information"
git clone https://gerrit.opnfv.org/gerrit/sdnvpn.git
pushd sdnvpn/odl-pipeline/lib > /dev/null
sudo ./tripleo_introspector.sh --out-file ${tmp_dir}/node.yaml
popd > /dev/null
sudo rm -rf sdnvpn

sudo chown jenkins-ci:jenkins-ci ${tmp_dir}/*

ls -lrt ${tmp_dir}

echo "Fetch complete"
