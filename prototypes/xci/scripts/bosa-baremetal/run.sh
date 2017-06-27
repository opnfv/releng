#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

INVENTORY=$1
export ANSIBLE_STDOUT_CALLBACK=debug


#-------------------------------------------------------------------------------
# Check run as root
#-------------------------------------------------------------------------------

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 1>&2
    exit
fi

#-------------------------------------------------------------------------------
# Check pod config
#-------------------------------------------------------------------------------

echo '---- Inventory ----'
cat $INVENTORY
echo '-------------------'
read -p "Do you confirm those parameters? (y/n) " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit
fi

#-------------------------------------------------------------------------------
# install ansible
#-------------------------------------------------------------------------------

apt-get install -y software-properties-common python-setuptools \
    python-dev libffi-dev libssl-dev git sshpass tree python-pip
pip install --upgrade pip
pip install cryptography
pip install ansible

#-------------------------------------------------------------------------------
# BIFROST
#-------------------------------------------------------------------------------

ansible-playbook -i $INVENTORY opnfv-bifrost-install.yaml
ansible-playbook -i $INVENTORY opnfv-bifrost-enroll-deploy.yaml

#-------------------------------------------------------------------------------
# Prepare nodes
#-------------------------------------------------------------------------------

ansible-playbook -i /etc/bosa/ansible_inventory opnfv-wait-for-nodes.yaml
ansible-playbook -i /etc/bosa/ansible_inventory opnfv-prepare-nodes.yaml

#-------------------------------------------------------------------------------
# Prepare OSA
#-------------------------------------------------------------------------------

ansible-playbook -i $INVENTORY opnfv-osa-prepare.yaml
pip uninstall -y ansible
/opt/openstack-ansible/scripts/bootstrap-ansible.sh
ansible-playbook -i $INVENTORY opnfv-osa-configure.yaml

#-------------------------------------------------------------------------------
# Run OSA
#-------------------------------------------------------------------------------

cd /opt/openstack-ansible/playbooks
openstack-ansible setup-hosts.yml
openstack-ansible setup-infrastructure.yml
ansible galera_container -m shell -a "mysql -h localhost -e 'show status like \"%wsrep_cluster_%\";'"
openstack-ansible setup-openstack.yml

#-------------------------------------------------------------------------------
# End
#-------------------------------------------------------------------------------
