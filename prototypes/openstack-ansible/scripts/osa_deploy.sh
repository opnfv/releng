#!/bin/bash

#set -x

export OSA_PATH=/opt/openstack-ansible
export LOG_PATH=$OSA_PATH/log
export PLAYBOOK_PATH=$OSA_PATH/playbooks

JUMPHOST_IP="192.168.122.2"

sudo /bin/rm -rf $LOG_PATH
sudo /bin/mkdir -p $LOG_PATH
sudo /bin/cp /root/.ssh/id_rsa.pub ../template/authorized_keys.temp

cd ../playbooks/
# this will preprae the jump host 
# such as, git clone the Openstack-Ansible and configure network
sudo ansible-playbook -i inventory jumphost_configuration.yml -vvv

# this will prepare the target host
# such as configure networki and NFS.
sudo ansible-playbook -i inventory targethost_configuration.yml

# using OpenStack-Ansible deploy the OpenStack after preparing

echo "set UP Host !"
sudo /bin/sh -c "ssh root@$JUMPHOST_IP openstack-ansible \
     $PLAYBOOK_PATH/setup-hosts.yml" | \
     tee $LOG_PATH/setup-host.log

#the first time runing it maybe unreachable
#if the nodes is unreachable run the playbook again
grep "unreachable=1" $LOG_PATH/setup-host.log>/dev/null
if [ $? -eq 0 ]; then
    sudo /bin/sh -c "ssh  root@$JUMPHOST_IP openstack-ansible \
         $PLAYBOOK_PATH/setup-hosts.yml" | \
         tee $LOG_PATH/setup-host.log
fi

#check the result of openstack-ansible setup-hosts.yml
#if failed, exit with exit code 1
grep "failed=1" $LOG_PATH/setup-host.log>/dev/null \
  ||  grep "unreachable=1" $LOG_PATH/setup-host.log>/dev/null
if [ $? -eq 0 ]; then
    echo "failed setup host!"
    exit 1
else
    echo "setup host successfully!"
fi

echo "Set UP Infrastructure !"

sudo /bin/sh -c "ssh root@$JUMPHOST_IP  openstack-ansible \
     $PLAYBOOK_PATH/setup-infrastructure.yml" | \
     tee $LOG_PATH/setup-infrastructure.log

grep "failed=1" $LOG_PATH/setup-infrastructure.log>/dev/null \
  ||  grep "unreachable=1" $LOG_PATH/setup-infrastructure.log>/dev/null
if [ $? -eq 0 ]; then
    echo "failed setup infrastructure!"
    exit 1
else
    echo "setup infrastructure successfully!"
fi

sudo /bin/sh -c "ssh root@$JUMPHOST_IP ansible -i $PLAYBOOK_PATH/inventory/ \
           galera_container -m shell \
           -a "mysql -h localhost -e 'show status like \"%wsrep_cluster_%\";'"" \
           | tee $LOG_PATH/galera.log

grep "FAILED" $LOG_PATH/galera.log>/dev/null
if [ $? -eq 0 ]; then
    echo "failed verify the database cluster!"
    exit 1
else
    echo "verify the database cluster successfully!"
fi

echo "Set UP OpenStack !"
sudo /bin/sh -c "ssh root@$JUMPHOST_IP openstack-ansible \
     $PLAYBOOK_PATH/setup-openstack.yml" | \
     tee  $LOG_PATH/setup-openstack.log

grep "failed=1" $LOG_PATH/setup-openstack.log>/dev/null \
   || grep "unreachable=1" $LOG_PATH/setup-openstack.log>/dev/null
if [ $? -eq 0 ]; then
   echo "failed setup openstack !"
   exit 1
else
   echo "setup Opesntack successfully!"
   exit 0
fi
