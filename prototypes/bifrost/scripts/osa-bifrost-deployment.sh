#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

set -eux
set -o pipefail
export PYTHONUNBUFFERED=1
SCRIPT_HOME="$(cd "$(dirname "$0")" && pwd)"
BIFROST_HOME=$SCRIPT_HOME/..
ANSIBLE_INSTALL_ROOT=${ANSIBLE_INSTALL_ROOT:-/opt/stack}
ENABLE_VENV="false"
USE_DHCP="false"
USE_VENV="false"
BUILD_IMAGE=true
PROVISION_WAIT_TIMEOUT=${PROVISION_WAIT_TIMEOUT:-3600}

# ensure the right inventory files is used based on branch
CURRENT_BIFROST_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ $CURRENT_BIFROST_BRANCH = "master" ]; then
    BAREMETAL_DATA_FILE=${BAREMETAL_DATA_FILE:-'/tmp/baremetal.json'}
    INVENTORY_FILE_FORMAT="baremetal_json_file"
else
    BAREMETAL_DATA_FILE=${BAREMETAL_DATA_FILE:-'/tmp/baremetal.csv'}
    INVENTORY_FILE_FORMAT="baremetal_csv_file"
fi
export BIFROST_INVENTORY_SOURCE=$BAREMETAL_DATA_FILE

# Set defaults for ansible command-line options to drive the different
# tests.

# NOTE(TheJulia/cinerama): The variables defined on the command line
# for the default and DHCP tests are to drive the use of Cirros as the
# deployed operating system, and as such sets the test user to cirros,
# and writes a debian style interfaces file out to the configuration
# drive as cirros does not support the network_info.json format file
# placed in the configuration drive. The "build image" test does not
# use cirros.

TEST_VM_NUM_NODES=6
export TEST_VM_NODE_NAMES="xcimaster controller00 controller01 controller02 compute00 compute01"
export VM_DOMAIN_TYPE="kvm"
# 8 vCPU, 60 GB HDD are minimum equipment
export VM_CPU=${VM_CPU:-8}
export VM_DISK=${VM_DISK:-100}
export VM_DISK_CACHE=${VM_DISK_CACHE:-unsafe}
TEST_PLAYBOOK="opnfv-virtual.yaml"
USE_INSPECTOR=true
USE_CIRROS=false
TESTING_USER=root
# seting the memory to 16 GB to make more easily success
# 8 GB RAM is minimum equipment, but it work with at least 12 GB.
VM_MEMORY_SIZE=${VM_MEMORY_SIZE:-16384}
DOWNLOAD_IPA=true
CREATE_IPA_IMAGE=false
INSPECT_NODES=true
INVENTORY_DHCP=false
INVENTORY_DHCP_STATIC_IP=false
WRITE_INTERFACES_FILE=true


# settings for console access
export DIB_DEV_USER_PWDLESS_SUDO=yes
export DIB_DEV_USER_PASSWORD=devuser

# settings for distro: trusty/ubuntu-minimal, 7/centos7
export DIB_OS_RELEASE=${DIB_OS_RELEASE:-xenial}
export DIB_OS_ELEMENT=${DIB_OS_ELEMENT:-ubuntu-minimal}

# for centos 7: "vim,less,bridge-utils,iputils,rsyslog,curl"
export DIB_OS_PACKAGES=${DIB_OS_PACKAGES:-"vlan,vim,less,bridge-utils,sudo,language-pack-en,iputils-ping,rsyslog,curl,python,debootstrap,ifenslave,ifenslave-2.6,lsof,lvm2,tcpdump,nfs-kernel-server,chrony"}

# Additional dib elements
export EXTRA_DIB_ELEMENTS=${EXTRA_DIB_ELEMENTS:-"openssh-server"}

# Source Ansible
# NOTE(TheJulia): Ansible stable-1.9 source method tosses an error deep
# under the hood which -x will detect, so for this step, we need to suspend
# and then re-enable the feature.
set +x +o nounset
$SCRIPT_HOME/env-setup.sh
source ${ANSIBLE_INSTALL_ROOT}/ansible/hacking/env-setup
ANSIBLE=$(which ansible-playbook)
set -x -o nounset

logs_on_exit() {
    $SCRIPT_HOME/collect-test-info.sh
}
trap logs_on_exit EXIT

# Change working directory
cd $BIFROST_HOME/playbooks

# Syntax check of dynamic inventory test path
for task in syntax-check list-tasks; do
    ${ANSIBLE} \
           -i inventory/localhost \
           test-bifrost-create-vm.yaml \
           --${task}
    ${ANSIBLE} \
           -i inventory/localhost \
           ${TEST_PLAYBOOK} \
           --${task} \
           -e testing_user=${TESTING_USER}
done

# Create the test VMS
${ANSIBLE} \
       -i inventory/localhost \
       test-bifrost-create-vm.yaml \
       -e test_vm_num_nodes=${TEST_VM_NUM_NODES} \
       -e test_vm_memory_size=${VM_MEMORY_SIZE} \
       -e enable_venv=${ENABLE_VENV} \
       -e test_vm_domain_type=${VM_DOMAIN_TYPE} \
       -e ${INVENTORY_FILE_FORMAT}=${BAREMETAL_DATA_FILE}

# Execute the installation and VM startup test.
${ANSIBLE} \
    -i inventory/bifrost_inventory.py \
    ${TEST_PLAYBOOK} \
    -e use_cirros=${USE_CIRROS} \
    -e testing_user=${TESTING_USER} \
    -e test_vm_num_nodes=${TEST_VM_NUM_NODES} \
    -e inventory_dhcp=${INVENTORY_DHCP} \
    -e inventory_dhcp_static_ip=${INVENTORY_DHCP_STATIC_IP} \
    -e enable_venv=${ENABLE_VENV} \
    -e enable_inspector=${USE_INSPECTOR} \
    -e inspect_nodes=${INSPECT_NODES} \
    -e download_ipa=${DOWNLOAD_IPA} \
    -e create_ipa_image=${CREATE_IPA_IMAGE} \
    -e write_interfaces_file=${WRITE_INTERFACES_FILE} \
    -e ipv4_gateway=192.168.122.1 \
    -e wait_timeout=${PROVISION_WAIT_TIMEOUT}
EXITCODE=$?

if [ $EXITCODE != 0 ]; then
    echo "****************************"
    echo "Test failed. See logs folder"
    echo "****************************"
fi

exit $EXITCODE
