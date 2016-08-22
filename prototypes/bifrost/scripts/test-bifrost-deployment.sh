# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
#!/bin/bash

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

# Set defaults for ansible command-line options to drive the different
# tests.

# NOTE(TheJulia/cinerama): The variables defined on the command line
# for the default and DHCP tests are to drive the use of Cirros as the
# deployed operating system, and as such sets the test user to cirros,
# and writes a debian style interfaces file out to the configuration
# drive as cirros does not support the network_info.json format file
# placed in the configuration drive. The "build image" test does not
# use cirros.

TEST_VM_NUM_NODES=3
export TEST_VM_NODE_NAMES="jumphost.opnfvlocal controller00.opnfvlocal compute00.opnfvlocal"
export VM_DOMAIN_TYPE="kvm"
export VM_CPU=4
export VM_DISK=100
TEST_PLAYBOOK="test-bifrost-infracloud.yaml"
USE_INSPECTOR=true
USE_CIRROS=false
TESTING_USER=root
VM_MEMORY_SIZE="8192"
DOWNLOAD_IPA=true
CREATE_IPA_IMAGE=false
INSPECT_NODES=true
INVENTORY_DHCP=false
INVENTORY_DHCP_STATIC_IP=false
WRITE_INTERFACES_FILE=true

# Set BIFROST_INVENTORY_SOURCE
export BIFROST_INVENTORY_SOURCE=/tmp/baremetal.csv

# DIB custom elements path
export ELEMENTS_PATH=/usr/share/diskimage-builder/elements:/opt/puppet-infracloud/files/elements

# settings for console access
export DIB_DEV_USER_PWDLESS_SUDO=yes
export DIB_DEV_USER_PASSWORD=devuser

# Source Ansible
# NOTE(TheJulia): Ansible stable-1.9 source method tosses an error deep
# under the hood which -x will detect, so for this step, we need to suspend
# and then re-enable the feature.
set +x +o nounset
$SCRIPT_HOME/env-setup.sh
source ${ANSIBLE_INSTALL_ROOT}/ansible/hacking/env-setup
ANSIBLE=$(which ansible-playbook)
set -x -o nounset

# Change working directory
cd $BIFROST_HOME/playbooks

# Syntax check of dynamic inventory test path
${ANSIBLE} -vvvv \
       -i inventory/localhost \
       test-bifrost-create-vm.yaml \
       --syntax-check \
       --list-tasks
${ANSIBLE} -vvvv \
       -i inventory/localhost \
       ${TEST_PLAYBOOK} \
       --syntax-check \
       --list-tasks \
       -e testing_user=${TESTING_USER}

# Create the test VMS
${ANSIBLE} -vvvv \
       -i inventory/localhost \
       test-bifrost-create-vm.yaml \
       -e test_vm_num_nodes=${TEST_VM_NUM_NODES} \
       -e test_vm_memory_size=${VM_MEMORY_SIZE} \
       -e enable_venv=${ENABLE_VENV} \
       -e test_vm_domain_type=${VM_DOMAIN_TYPE}

# Execute the installation and VM startup test.
${ANSIBLE} -vvvv \
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
    -e ipv4_gateway=192.168.122.1
EXITCODE=$?

if [ $EXITCODE != 0 ]; then
    echo "****************************"
    echo "Test failed. See logs folder"
    echo "****************************"
fi

$SCRIPT_HOME/collect-test-info.sh

exit $EXITCODE
