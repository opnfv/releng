#!/bin/bash
#TODO
export WORK_PATH=$(pwd)

source ./var/env_var.sh

source ./prepare.sh

set -x

sudo rm -rf $OSA_PATH $OSA_ETC_PATH
sudo git clone https://git.openstack.org/openstack/openstack-ansible $OSA_PATH

cd $OSA_PATH
sudo ./scripts/bootstrap-ansible.sh
sudo /bin/cp -rf $OSA_PATH/etc/openstack_deploy $OSA_ETC_PATH

cd /opt/openstack-ansible/scripts/
sudo python pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml

cd $WORK_PATH

sudo /bin/cp -rf ./template/openstack_user_config.yml.temp $OSA_ETC_PATH/openstack_user_config.yml

sudo /bin/cp -rf ./template/user_variables.yml.temp $OSA_ETC_PATH/user_variables.yml

sudo /bin/cp -rf ./template/cinder.yml.temp $OSA_ETC_PATH/env.d/cinder.yml

sudo ansible-playbook -i inventory playbook.yml

source ./OpenStackAnsible.sh
