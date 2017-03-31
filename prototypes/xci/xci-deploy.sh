#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# This script must run as root
if [[ $(whoami) != "root" ]]; then
    echo "Error: This script must be run as root!"
    exit 1
fi

# find where are we
XCI_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# source user vars
source $XCI_PATH/config/user-vars

# source pinned versions
source $XCI_PATH/config/pinned-versions

# source flavor configuration
source "$XCI_PATH/flavors/${XCI_FLAVOR}-vars"

# source xci configuration
source $XCI_PATH/config/env-vars

# log info to console
echo "Info: Starting XCI Deployment"
echo "Info: Deployment parameters"
echo "-------------------------------------------------------------------------"
echo "xci flavor: $XCI_FLAVOR"
echo "opnfv/releng version: $OPNFV_RELENG_VERSION"
echo "openstack/bifrost version: $OPENSTACK_BIFROST_VERSION"
echo "openstack/openstack-ansible version: $OPENSTACK_OSA_VERSION"
echo "-------------------------------------------------------------------------"

#-------------------------------------------------------------------------------
# install ansible on localhost
#-------------------------------------------------------------------------------
pip install ansible==$XCI_ANSIBLE_PIP_VERSION

#-------------------------------------------------------------------------------
# Start provisioning VM nodes
#-------------------------------------------------------------------------------
echo "Info: Starting provisining VM nodes using openstack/bifrost"
echo "      This might take between 10 to 20 minutes depending on the flavor and the host"
echo "-------------------------------------------------------------------------"
cd $XCI_PATH/playbooks
STARTTIME=$(date +%s)
ansible-playbook $ANSIBLE_VERBOSITY -i inventory provision-vm-nodes.yml
ENDTIME=$(date +%s)
echo "-----------------------------------------------------------------------"
echo "Info: VM nodes are provisioned!"
echo "Info: It took $(($ENDTIME - $STARTTIME)) seconds to provising the VM nodes"
