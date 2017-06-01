#!/usr/bin/env bash
##############################################################################
# Copyright (c) 2016 Tim Rozet (Red Hat) and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

set -o errexit
set -o nounset
set -o pipefail

SSH_OPTIONS=(-o StrictHostKeyChecking=no -o GlobalKnownHostsFile=/dev/null -o UserKnownHostsFile=/dev/null -o LogLevel=error)

if [ -z "$SNAP_TYPE" ]; then
  echo "ERROR: SNAP_TYPE not provided...exiting"
  exit 1
fi

echo "Creating Apex snapshot..."
echo "-------------------------"
echo

# create tmp directory
tmp_dir=$(pwd)/.tmp
mkdir -p ${tmp_dir}

# TODO(trozet) remove this after fix goes in for tripleo_inspector to copy these
pushd ${tmp_dir} > /dev/null
echo "Copying overcloudrc and ssh key from Undercloud..."
# Store overcloudrc
UNDERCLOUD=$(sudo virsh domifaddr undercloud | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
sudo scp ${SSH_OPTIONS[@]} stack@${UNDERCLOUD}:overcloudrc ./
# Copy out ssh key of stack from undercloud
sudo scp ${SSH_OPTIONS[@]} stack@${UNDERCLOUD}:.ssh/id_rsa ./
popd > /dev/null

echo "Gathering introspection information"
git clone https://gerrit.opnfv.org/gerrit/sdnvpn.git
pushd sdnvpn/odl-pipeline/lib > /dev/null
sudo ./tripleo_introspector.sh --out-file ${tmp_dir}/node.yaml
popd > /dev/null
sudo rm -rf sdnvpn

echo "Shutting down nodes"
# Shut down nodes
nodes=$(sudo virsh list | grep -Eo "baremetal[0-9]")
for node in $nodes; do
  sudo virsh shutdown ${node} --mode acpi
done

for node in $nodes; do
  count=0
  while [ "$count" -lt 10 ]; do
    sleep 10
    if sudo virsh list | grep ${node}; then
       echo "Waiting for $node to shutdown, try $count"
    else
       break
    fi
    count=$((count+1))
  done

  if [ "$count" -ge 10 ]; then
    echo "Node $node failed to shutdown"
    exit 1
  fi
done

pushd ${tmp_dir} > /dev/null
echo "Gathering virsh definitions"
# copy qcow2s, virsh definitions
for node in $nodes; do
  sudo cp -f /var/lib/libvirt/images/${node}.qcow2 ./
  sudo virsh dumpxml ${node} > ${node}.xml
done

# copy virsh net definitions
for net in admin api external storage tenant; do
  sudo virsh net-dumpxml ${net} > ${net}.xml
done

sudo chown jenkins-ci:jenkins-ci *

# tar up artifacts
DATE=`date +%Y-%m-%d`
tar czf ../apex-${SNAP_TYPE}-snap-${DATE}.tar.gz .
popd > /dev/null
sudo rm -rf ${tmp_dir}
echo "Snapshot saved as apex-${SNAP_TYPE}-snap-${DATE}.tar.gz"

# update opnfv properties file
if [ "$SNAP_TYPE" == 'csit' ]; then
  curl -O -L http://$GS_URL/snapshot.properties
  sed -i '/^OPNFV_SNAP_URL=/{h;s#=.*#='${GS_URL}'/apex-csit-snap-'${DATE}'.tar.gz#};${x;/^$/{s##OPNFV_SNAP_URL='${GS_URL}'/apex-csit-snap-'${DATE}'.tar.gz#;H};x}' snapshot.properties
  snap_sha=$(sha512sum apex-csit-snap-${DATE}.tar.gz | cut -d' ' -f1)
  sed -i '/^OPNFV_SNAP_SHA512SUM=/{h;s/=.*/='${snap_sha}'/};${x;/^$/{s//OPNFV_SNAP_SHA512SUM='${snap_sha}'/;H};x}' snapshot.properties
  echo "OPNFV_SNAP_URL=$GS_URL/apex-csit-snap-${DATE}.tar.gz"
  echo "OPNFV_SNAP_SHA512SUM=$(sha512sum apex-csit-snap-${DATE}.tar.gz | cut -d' ' -f1)"
  echo "Updated properties file: "
  cat snapshot.properties
fi
