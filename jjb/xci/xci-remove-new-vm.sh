#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 SUSE and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

declare -r VM_NAME=${DISTRO}_xci_vm

echo "Destroying previous '${VM_NAME}' instances..."
sudo virsh destroy ${VM_NAME} || true
sudo virsh undefine ${VM_NAME} || true
