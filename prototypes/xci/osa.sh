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

# source pinned versions
source $XCI_PATH/config/pinned-versions

# source user vars
source $XCI_PATH/config/user-vars

# source flavor configuration
source $XCI_PATH/config/$XCI_FLAVOR

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
cd $XCI_PATH/playbooks
ansible-playbook $ANSIBLE_VERBOSITY -i inventory configure-xcihost.yml --check
