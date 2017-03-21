#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Huawei Technologies Co.,Ltd and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

export OSA_PATH=/opt/openstack-ansible
export LOG_PATH=$OSA_PATH/log
export PLAYBOOK_PATH=$OSA_PATH/playbooks
export OSA_BRANCH=${OSA_BRANCH:-"master"}
XCIMASTER_IP="192.168.122.2"

sudo /bin/rm -rf $LOG_PATH
sudo /bin/mkdir -p $LOG_PATH
sudo /bin/cp /root/.ssh/id_rsa.pub ../file/authorized_keys
echo -e '\n' | sudo tee --append ../file/authorized_keys

# log some info
echo -e "\n"
echo "***********************************************************************"
echo "*                                                                     *"
echo "*                        Configure XCI Master                         *"
echo "*                                                                     *"
echo "*  Bootstrap xci-master, configure network, clone openstack-ansible   *"
echo "*                                                                     *"
echo "***********************************************************************"
echo -e "\n"

cd ../playbooks/
# this will prepare the jump host
# git clone the Openstack-Ansible, bootstrap and configure network
sudo -E ansible-playbook -i inventory configure-xcimaster.yml

echo "XCI Master is configured successfully!"

# log some info
echo -e "\n"
echo "***********************************************************************"
echo "*                                                                     *"
echo "*                          Configure Nodes                            *"
echo "*                                                                     *"
echo "*       Configure network on OpenStack Nodes, configure NFS           *"
echo "*                                                                     *"
echo "***********************************************************************"
echo -e "\n"

# this will prepare the target host
# such as configure network and NFS
sudo -E ansible-playbook -i inventory configure-targethosts.yml

echo "Nodes are configured successfully!"

# log some info
echo -e "\n"
echo "***********************************************************************"
echo "*                                                                     *"
echo "*                       Set Up OpenStack Nodes                        *"
echo "*                                                                     *"
echo "*            Set up OpenStack Nodes using openstack-ansible           *"
echo "*                                                                     *"
echo "***********************************************************************"
echo -e "\n"

# using OpenStack-Ansible deploy the OpenStack

sudo -E /bin/sh -c "ssh root@$XCIMASTER_IP openstack-ansible \
     $PLAYBOOK_PATH/setup-hosts.yml" | \
     tee $LOG_PATH/setup-host.log

#check the result of openstack-ansible setup-hosts.yml
#if failed, exit with exit code 1
grep "failed=1" $LOG_PATH/setup-host.log>/dev/null \
  || grep "unreachable=1" $LOG_PATH/setup-host.log>/dev/null
if [ $? -eq 0 ]; then
    echo "OpenStack node setup failed!"
    exit 1
fi

sudo -E /bin/sh -c "ssh root@$XCIMASTER_IP openstack-ansible \
     $PLAYBOOK_PATH/setup-infrastructure.yml" | \
     tee $LOG_PATH/setup-infrastructure.log

grep "failed=1" $LOG_PATH/setup-infrastructure.log>/dev/null \
  || grep "unreachable=1" $LOG_PATH/setup-infrastructure.log>/dev/null
if [ $? -eq 0 ]; then
    echo "failed setup infrastructure!"
    exit 1
fi

echo "OpenStack nodes are setup successfully!"

sudo -E /bin/sh -c "ssh root@$XCIMASTER_IP ansible -i $PLAYBOOK_PATH/inventory/ \
           galera_container -m shell \
           -a "mysql -h localhost -e 'show status like \"%wsrep_cluster_%\";'"" \
           | tee $LOG_PATH/galera.log

grep "FAILED" $LOG_PATH/galera.log>/dev/null
if [ $? -eq 0 ]; then
    echo "Database cluster verification failed!"
    exit 1
else
    echo "Database cluster verification successful!"
fi

# log some info
echo -e "\n"
echo "***********************************************************************"
echo "*                                                                     *"
echo "*                           Install OpenStack                         *"
echo "*                                                                     *"
echo "***********************************************************************"
echo -e "\n"

sudo -E /bin/sh -c "ssh root@$XCIMASTER_IP openstack-ansible \
     $PLAYBOOK_PATH/setup-openstack.yml" | \
     tee $LOG_PATH/setup-openstack.log

grep "failed=1" $LOG_PATH/setup-openstack.log>/dev/null \
  || grep "unreachable=1" $LOG_PATH/setup-openstack.log>/dev/null
if [ $? -eq 0 ]; then
   echo "OpenStack installation failed!"
   exit 1
else
   echo "OpenStack installation is successfully completed!"
   exit 0
fi
