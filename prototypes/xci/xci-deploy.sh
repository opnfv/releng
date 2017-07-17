#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

#-------------------------------------------------------------------------------
# This script should not be run as root
#-------------------------------------------------------------------------------
if [[ $(whoami) == "root" ]]; then
    echo "WARNING: This script should not be run as root!"
    echo "Elevated privileges are aquired automatically when necessary"
    echo "Waiting 10s to give you a chance to stop the script (Ctrl-C)"
    for x in $(seq 10 -1 1); do echo -n "$x..."; sleep 1; done
fi

#-------------------------------------------------------------------------------
# Set environment variables
#-------------------------------------------------------------------------------
# The order of sourcing the variable files is significant so please do not
# change it or things might stop working.
# - user-vars: variables that can be configured or overriden by user.
# - pinned-versions: versions to checkout. These can be overriden if you want to
#   use different/more recent versions of the tools but you might end up using
#   something that is not verified by OPNFV XCI.
# - flavor-vars: settings for VM nodes for the chosen flavor.
# - env-vars: variables for the xci itself and you should not need to change or
#   override any of them.
#-------------------------------------------------------------------------------
# find where are we
XCI_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# source user vars
source $XCI_PATH/config/user-vars
# source pinned versions
source $XCI_PATH/config/pinned-versions
# source flavor configuration
source "$XCI_PATH/config/${XCI_FLAVOR}-vars"
# source xci configuration
source $XCI_PATH/config/env-vars

#-------------------------------------------------------------------------------
# Sanitize local development environment variables
#-------------------------------------------------------------------------------
user_local_dev_vars=(OPNFV_RELENG_DEV_PATH OPNFV_OSA_DEV_PATH OPNFV_BIFROST_DEV_PATH)
for local_user_var in ${user_local_dev_vars[@]}; do
    [[ -n ${!local_user_var:-} ]] && export $local_user_var=${!local_user_var%/}/
done
unset user_local_dev_vars local_user_var

#-------------------------------------------------------------------------------
# Log info to console
#-------------------------------------------------------------------------------
echo "Info: Starting XCI Deployment"
echo "Info: Deployment parameters"
echo "-------------------------------------------------------------------------"
echo "xci flavor: $XCI_FLAVOR"
echo "opnfv/releng version: $OPNFV_RELENG_VERSION"
echo "openstack/bifrost version: $OPENSTACK_BIFROST_VERSION"
echo "openstack/openstack-ansible version: $OPENSTACK_OSA_VERSION"
echo "-------------------------------------------------------------------------"

#-------------------------------------------------------------------------------
# Install ansible on localhost
#-------------------------------------------------------------------------------
source file/install-ansible.sh

# TODO: The xci playbooks can be put into a playbook which will be done later.

#-------------------------------------------------------------------------------
# Start provisioning VM nodes
#-------------------------------------------------------------------------------
# This playbook
# - removes directories that were created by the previous xci run
# - clones opnfv/releng and openstack/bifrost repositories
# - combines opnfv/releng and openstack/bifrost scripts/playbooks
# - destorys VMs, removes ironic db, leases, logs
# - creates and provisions VMs for the chosen flavor
#-------------------------------------------------------------------------------
echo "Info: Starting provisining VM nodes using openstack/bifrost"
echo "-------------------------------------------------------------------------"
cd $XCI_PATH/playbooks
ansible-playbook $ANSIBLE_VERBOSITY -i inventory provision-vm-nodes.yml
echo "-----------------------------------------------------------------------"
echo "Info: VM nodes are provisioned!"
source $OPENSTACK_BIFROST_PATH/env-vars
ironic node-list
echo
#-------------------------------------------------------------------------------
# Configure localhost
#-------------------------------------------------------------------------------
# This playbook
# - removes directories that were created by the previous xci run
# - clones opnfv/releng repository
# - creates log directory
# - copies flavor files such as playbook, inventory, and var file
#-------------------------------------------------------------------------------
echo "Info: Configuring localhost for openstack-ansible"
echo "-----------------------------------------------------------------------"
cd $XCI_PATH/playbooks
ansible-playbook $ANSIBLE_VERBOSITY -i inventory configure-localhost.yml
echo "-----------------------------------------------------------------------"
echo "Info: Configured localhost host for openstack-ansible"

#-------------------------------------------------------------------------------
# Configure openstack-ansible deployment host, opnfv
#-------------------------------------------------------------------------------
# This playbook
# - removes directories that were created by the previous xci run
# - clones opnfv/releng and openstack/openstack-ansible repositories
# - configures network
# - generates/prepares ssh keys
# - bootstraps ansible
# - copies flavor files to be used by openstack-ansible
#-------------------------------------------------------------------------------
echo "Info: Configuring opnfv deployment host for openstack-ansible"
echo "-----------------------------------------------------------------------"
cd ${XCI_DEVEL_ROOT}
ansible-playbook $ANSIBLE_VERBOSITY -i ${OPNFV_RELENG_PATH}/prototypes/xci/playbooks/inventory ${OPNFV_RELENG_PATH}/prototypes/xci/playbooks/configure-opnfvhost.yml
echo "-----------------------------------------------------------------------"
echo "Info: Configured opnfv deployment host for openstack-ansible"

#-------------------------------------------------------------------------------
# Skip the rest if the flavor is aio since the target host for aio is opnfv
#-------------------------------------------------------------------------------
if [[ $XCI_FLAVOR == "aio" ]]; then
    echo "xci: aio has been installed"
    exit 0
fi

#-------------------------------------------------------------------------------
# Configure target hosts for openstack-ansible
#-------------------------------------------------------------------------------
# This playbook
# - adds public keys to target hosts
# - configures network
# - configures nfs
#-------------------------------------------------------------------------------
echo "Info: Configuring target hosts for openstack-ansible"
echo "-----------------------------------------------------------------------"
cd $OPNFV_RELENG_PATH/prototypes/xci/playbooks
ansible-playbook $ANSIBLE_VERBOSITY -i inventory configure-targethosts.yml
echo "-----------------------------------------------------------------------"
echo "Info: Configured target hosts"

#-------------------------------------------------------------------------------
# Set up target hosts for openstack-ansible
#-------------------------------------------------------------------------------
# This is openstack-ansible playbook. Check upstream documentation for details.
#-------------------------------------------------------------------------------
echo "Info: Setting up target hosts for openstack-ansible"
echo "-----------------------------------------------------------------------"
ssh root@$OPNFV_HOST_IP "openstack-ansible \
     $OPENSTACK_OSA_PATH/playbooks/setup-hosts.yml" | \
     tee $LOG_PATH/setup-hosts.log
echo "-----------------------------------------------------------------------"
# check the log to see if we have any error
if grep -q 'failed=1\|unreachable=1' $LOG_PATH/setup-hosts.log; then
    echo "Error: OpenStack node setup failed!"
    exit 1
fi
echo "Info: Set up target hosts for openstack-ansible successfuly"

#-------------------------------------------------------------------------------
# Set up infrastructure
#-------------------------------------------------------------------------------
# This is openstack-ansible playbook. Check upstream documentation for details.
#-------------------------------------------------------------------------------
echo "Info: Setting up infrastructure"
echo "-----------------------------------------------------------------------"
echo "xci: running ansible playbook setup-infrastructure.yml"
ssh root@$OPNFV_HOST_IP "openstack-ansible \
     $OPENSTACK_OSA_PATH/playbooks//setup-infrastructure.yml" | \
     tee $LOG_PATH/setup-infrastructure.log
echo "-----------------------------------------------------------------------"
# check the log to see if we have any error
if grep -q 'failed=1\|unreachable=1' $LOG_PATH/setup-infrastructure.log; then
    echo "Error: OpenStack node setup failed!"
    exit 1
fi

#-------------------------------------------------------------------------------
# Verify database cluster
#-------------------------------------------------------------------------------
echo "Info: Verifying database cluster"
echo "-----------------------------------------------------------------------"
ssh root@$OPNFV_HOST_IP "ansible -i $OPENSTACK_OSA_PATH/playbooks/inventory/ \
           galera_container -m shell \
           -a "mysql -h localhost -e 'show status like \"%wsrep_cluster_%\";'"" \
           | tee $LOG_PATH/galera.log
echo "-----------------------------------------------------------------------"
# check the log to see if we have any error
if grep -q 'FAILED' $LOG_PATH/galera.log; then
    echo "Error: Database cluster verification failed!"
    exit 1
fi
echo "Info: Database cluster verification successful!"

#-------------------------------------------------------------------------------
# Install OpenStack
#-------------------------------------------------------------------------------
# This is openstack-ansible playbook. Check upstream documentation for details.
#-------------------------------------------------------------------------------
echo "Info: Installing OpenStack on target hosts"
echo "-----------------------------------------------------------------------"
ssh root@$OPNFV_HOST_IP "openstack-ansible \
     $OPENSTACK_OSA_PATH/playbooks/setup-openstack.yml" | \
     tee $LOG_PATH/opnfv-setup-openstack.log
echo "-----------------------------------------------------------------------"
# check the log to see if we have any error
if grep -q 'failed=1\|unreachable=1' $LOG_PATH/opnfv-setup-openstack.log; then
   echo "Error: OpenStack installation failed!"
   exit 1
fi
echo "Info: OpenStack installation is successfully completed!"
