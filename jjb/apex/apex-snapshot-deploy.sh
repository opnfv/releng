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
SNAP_CACHE=$HOME/snap_cache


echo "Deploying Apex snapshot..."
echo "--------------------------"
echo

echo "Cleaning server"
pushd ci > /dev/null
sudo opnfv-clean
popd > /dev/null

echo "Downloading latest snapshot properties file"
if ! wget -O $WORKSPACE/opnfv.properties http://$GS_URL/snapshot.properties; then
  echo "ERROR: Unable to find snapshot.properties at ${GS_URL}...exiting"
  exit 1
fi

# find latest check sum
latest_snap_checksum=$(cat opnfv.properties | grep OPNFV_SNAP_SHA512SUM | awk -F "=" '{print $2}')
if [ -z "$latest_snap_checksum" ]; then
  echo "ERROR: checksum of latest snapshot from snapshot.properties is null!"
  exit 1
fi

local_snap_checksum=""

# check snap cache directory exists
# if snapshot cache exists, find the checksum
if [ -d "$SNAP_CACHE" ]; then
  latest_snap=$(ls ${SNAP_CACHE} | grep tar.gz | tail -n 1)
  if [ -n "$latest_snap" ]; then
    local_snap_checksum=$(sha512sum ${SNAP_CACHE}/${latest_snap} | cut -d' ' -f1)
  fi
else
  mkdir -p ${SNAP_CACHE}
fi

# compare check sum and download latest snap if not up to date
if [ "$local_snap_checksum" != "$latest_snap_checksum" ]; then
  snap_url=$(cat opnfv.properties | grep OPNFV_SNAP_URL | awk -F "=" '{print $2}')
  if [ -z "$snap_url" ]; then
    echo "ERROR: Snap URL from snapshot.properties is null!"
    exit 1
  fi
  echo "INFO: SHA mismatch, will download latest snapshot"
  # wipe cache
  rm -rf ${SNAP_CACHE}/*
  wget --directory-prefix=${SNAP_CACHE}/ ${snap_url}
  snap_tar=$(basename ${snap_url})
else
  snap_tar=${latest_snap}
fi

echo "INFO: Snapshot to be used is ${snap_tar}"

# move to snap cache dir and unpack
pushd ${SNAP_CACHE} > /dev/null
tar xvf ${snap_tar}

# create each network
virsh_networks=$(ls *.xml | grep -v baremetal)

if [ -z "$virsh_networks" ]; then
  echo "ERROR: no virsh networks found in snapshot unpack"
  exit 1
fi

echo "Checking overcloudrc"
if ! stat overcloudrc; then
  echo "ERROR: overcloudrc does not exist in snap unpack"
  exit 1
fi

for network_def in ${virsh_networks}; do
  sudo virsh net-create ${network_def}
  network=$(echo ${network_def} | awk -F '.' '{print $1}')
  if ! sudo virsh net-list | grep ${network}; then
    sudo virsh net-start ${network}
  fi
  echo "Checking if OVS bridge is missing for network: ${network}"
  if ! sudo ovs-vsctl show | grep "br-${network}"; then
    sudo ovs-vsctl add-br br-${network}
    echo "OVS Bridge created: br-${network}"
    if [ "br-${network}" == 'br-admin' ]; then
      echo "Configuring IP 192.0.2.99 on br-admin"
      sudo ip addr add  192.0.2.99/24 dev br-admin
      sudo ip link set up dev br-admin
    elif [ "br-${network}" == 'br-external' ]; then
      echo "Configuring IP 192.168.37.1 on br-external"
      sudo ip addr add  192.168.37.1/24 dev br-external
      sudo ip link set up dev br-external
      # Routes for admin network
      # The overcloud controller is multi-homed and will fail to respond
      # to traffic from the functest container due to reverse-path-filtering
      # This route allows reverse traffic, by forcing admin network destined
      # traffic through the external network for controller IPs only.
      # Compute nodes have no ip on external interfaces.
      controller_ips=$(cat overcloudrc | grep -Eo "192.0.2.[0-9]+")
      for ip in $controller_ips; do
        sudo ip route add ${ip}/32 dev br-external
      done
    fi
  fi
done

echo "Virsh networks up: $(sudo virsh net-list)"
echo "Bringing up Overcloud VMs..."
virsh_vm_defs=$(ls baremetal*.xml)

if [ -z "$virsh_vm_defs" ]; then
  echo "ERROR: no virsh VMs found in snapshot unpack"
  exit 1
fi

for node_def in ${virsh_vm_defs}; do
  sed  -ri "s/machine='[^\s]+'/machine='pc'/" ${node_def}
  sudo virsh define ${node_def}
  node=$(echo ${node_def} | awk -F '.' '{print $1}')
  sudo cp -f ${node}.qcow2 /var/lib/libvirt/images/
  # FIXME (trozet) install java on each disk image as required to upgrade ODL
  # should be added to Apex as part of the deployment. Remove this after that
  # is complete
  sudo LIBGUESTFS_BACKEND=direct virt-customize --install java-1.8.0-openjdk -a /var/lib/libvirt/images/${node}.qcow2
  sudo virsh start ${node}
  echo "Node: ${node} started"
done

# copy overcloudrc for functest
mkdir -p $HOME/cloner-info
cp -f overcloudrc $HOME/cloner-info/

admin_controller_ip=$(cat overcloudrc | grep -Eo -m 1 "192.0.2.[0-9]+" | head -1)
netvirt_url="http://${admin_controller_ip}:8081/restconf/operational/network-topology:network-topology/topology/netvirt:1"

source overcloudrc
counter=1
while [ "$counter" -le 10 ]; do
  echo "Checking if OpenStack is up"
  if nc -z ${admin_controller_ip} 9696 > /dev/null; then
    echo "Overcloud Neutron is up...Checking if OpenDaylight NetVirt is up..."
    if curl --fail --silent -u admin:admin ${netvirt_url} > /dev/null; then
      echo "OpenDaylight is up.  Overcloud deployment complete"
      exit 0
    else
      echo "OpenDaylight not yet up, try ${counter}"
    fi
  else
    echo "Neutron not yet up, try ${counter}"
  fi
  counter=$((counter+1))
  sleep 60
done

echo "ERROR: Deployment not up after 10 minutes...exiting."
exit 1
