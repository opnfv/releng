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
# Cleanup the leftovers from the previous deployment
#-------------------------------------------------------------------------------
echo "Info: Cleaning up the previous deployment"
$XCI_PATH/../bifrost/scripts/destroy-env.sh > /dev/null 2>&1
/bin/rm -rf /opt/releng /opt/bifrost /opt/openstack-ansible /opt/stack

#-------------------------------------------------------------------------------
# Clone the repositories and checkout the versions
#-------------------------------------------------------------------------------
echo "Info: Cloning repositories and checking out versions"
git clone --quiet $OPNFV_RELENG_GIT_URL $OPNFV_RELENG_PATH && \
    cd $OPNFV_RELENG_PATH
echo "Info: Cloned opnfv/releng. HEAD currently points at"
echo "      $(git show --oneline -s --pretty=format:'%h - %s (%cr) <%an>')"
git clone --quiet $OPENSTACK_BIFROST_GIT_URL $OPENSTACK_BIFROST_PATH && \
    cd $OPENSTACK_BIFROST_PATH
echo "Info: Cloned openstack/bifrost. HEAD currently points at"
echo "      $(git show --oneline -s --pretty=format:'%h - %s (%cr) <%an>')"

#-------------------------------------------------------------------------------
# Combine opnfv and upstream scripts/playbooks
#-------------------------------------------------------------------------------
echo "Info: Combining opnfv/releng and opestack/bifrost scripts/playbooks"
/bin/cp -rf $OPNFV_RELENG_PATH/prototypes/bifrost/* $OPENSTACK_BIFROST_PATH/

#-------------------------------------------------------------------------------
# Start provisioning VM nodes
#-------------------------------------------------------------------------------
echo "Info: Starting provisining VM nodes using openstack/bifrost"
echo "      This might take between 10 to 20 minutes depending on the flavor and the host"
echo "-------------------------------------------------------------------------"
cd $OPENSTACK_BIFROST_PATH
STARTTIME=$(date +%s)
./scripts/bifrost-provision.sh
ENDTIME=$(date +%s)
echo "-----------------------------------------------------------------------"
echo "Info: VM nodes are provisioned!"
echo "Info: It took $(($ENDTIME - $STARTTIME)) seconds to provising the VM nodes"
