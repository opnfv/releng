#!/bin/bash

cd $PLAYBOOK_PATH
#cd /opt/openstack-ansible/playbooks  #test

figlet -ctf slant Set UP Host !

sudo openstack-ansible setup-hosts.yml | tee /home/setup-host.log

grep "unreachable=1" /home/setup-host.log>/dev/null
if [ $? -eq 0 ]; then
    sudo openstack-ansible setup-hosts.yml | tee /home/setup-host.log
fi

grep "failed=1" /home/setup-host.log>/dev/null
if [ $? -eq 0 ]; then
    echo "failed retry setup-host!"
    exit 1
fi


figlet -ctf slant Set UP Infrastructure !

sudo openstack-ansible setup-infrastructure.yml | tee /home/setup-infrastructure.log

grep "failed=1" /home/setup-infrastructure.log>/dev/null
if [ $? -eq 0 ]; then
    echo "failed retry setup-infrastructure!"
    exit 1
fi
sudo ansible galera_container -m shell \
  -a "mysql -h localhost -e 'show status like \"%wsrep_cluster_%\";'" | tee /home/galera.log

grep "FAILED" /home/galera.log>/dev/null
if [ $? -eq 0 ]; then
    echo "failed retry!"
    exit 1
fi

figlet -ctf slant Set UP OpenStack !
sudo openstack-ansible setup-openstack.yml | tee  /home/setup-openstack.log
grep "failed=1" /home/setup-openstack.log>/dev/null
if [ $? -eq 0 ]; then
   echo "failed retry setup-openstack !"
fi
