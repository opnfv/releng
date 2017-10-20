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

git clone https://git.openstack.org/openstack/bifrost $WORKSPACE/bifrost
git clone https://gerrit.opnfv.org/gerrit/releng-xci $WORKSPACE/releng-xci

# checkout the patch
cd $CLONE_LOCATION
git fetch $PROJECT_REPO $GERRIT_REFSPEC && sudo git checkout FETCH_HEAD

# combine opnfv and upstream scripts/playbooks
/bin/cp -rf $WORKSPACE/releng-xci/bifrost/* $WORKSPACE/bifrost/

cd $WORKSPACE/releng-xci
cat > bifrost_test.sh<<EOF
cd ~/bifrost
# provision 3 VMs; xcimaster, controller, and compute
./scripts/bifrost-provision.sh

# list the provisioned VMs
source env-vars
ironic node-list
sudo -H -E virsh list
EOF
chmod a+x bifrost_test.sh

# Fix up distros
case ${DISTRO} in
	xenial) VM_DISTRO=ubuntu ;;
	centos7) VM_DISTRO=centos ;;
	*suse*) VM_DISTRO=opensuse ;;
esac

./xci/scripts/vm/start-new-vm.sh $VM_DISTRO

rsync -a $WORKSPACE/releng-xci ${VM_DISTRO}_xci_vm:~/bifrost

ssh -F $HOME/.ssh/xci-vm-config ${VM_DISTRO}_xci_vm "cd ~/bifrost && ./bifrost_test.sh"
