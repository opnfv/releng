#!/bin/bash

if [[ $(whoami) != "root" ]]; then
    echo "Error: This script must be run as root!"
    exit 1
fi

# remove previously cloned repos
/bin/rm -rf /opt/bifrost /opt/puppet-infracloud /opt/releng

# clone upstream repos
git clone https://git.openstack.org/openstack/bifrost /opt/bifrost
git clone https://git.openstack.org/openstack-infra/puppet-infracloud /opt/puppet-infracloud

# temporary fix until https://review.openstack.org/#/c/354813/ is submitted
cd /opt/bifrost
git fetch https://git.openstack.org/openstack/bifrost refs/changes/13/354813/6 && git checkout FETCH_HEAD

# clone opnfv releng repo
git clone https://gerrit.opnfv.org/gerrit/releng /opt/releng

# combine opnfv and upstream scripts/playbooks
cp -R /opt/releng/prototypes/bifrost/* /opt/bifrost/

# cleanup remnants of previous deployment
cd /opt/bifrost
./scripts/destroy_env.sh

exit 0
# provision 3 VMs; jumphost, controller, and compute
cd /opt/bifrost
./scripts/test-bifrost-deployment.sh

# list the provisioned VMs
cd /opt/bifrost
source env-vars
ironic node-list
virsh list
