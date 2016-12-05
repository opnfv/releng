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

echo "Creating Apex snapshot..."
echo "-------------------------"
echo

# create tmp directory
mkdir -p ./.tmp
pushd ./.tmp > /dev/null
echo "Copying overcloudrc and ssh key from Undercloud..."
# Store overcloudrc
UNDERCLOUD=$(virsh domifaddr undercloud | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]')
scp stack@${UNDERCLOUD}:overcloudrc ./
# Copy out ssh key of stack from undercloud
scp stack@${UNDERCLOUD}:.ssh/id_rsa ./
echo "Shutting down nodes"
# Shut down nodes
nodes=$(sudo virsh list | grep -Eo "baremetal[0-9]")
for node in nodes; do
  sudo virsh shutdown node
done

for node in nodes; do
  count=0
  while "$count" < 10; do
    sleep 10
    if virsh list | grep node; then
       echo "Waiting for $node to shutdown, try $count"
    else
       break
    fi
    count=$((count+1))
  done

  if [ "$count" >= 10 ]; then
    echo "Node $node failed to shutdown"
    exit 1
  fi
done

# copy qcow2s, virsh definitions
for node in nodes; do
  cp -f /var/lib/libvirt/images/${node}.qcow2 ./
  sudo virsh dumpxml ${node} > ${node}.xml
done

# copy virsh net definitions
for net in "admin api external storage tenant"; do
  sudo virsh net-dumpxml ${net} > ${net}.xml
done

# tar up artifacts
DATE=`date +%Y-%m-%d`
popd > /dev/null
tar czf apex-csit-snap-${DATE}.tar.gz ./tmp/*
rm -rf ./tmp
