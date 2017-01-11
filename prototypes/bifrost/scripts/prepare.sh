#!/bin/bash
set -x

sudo apt-get update

sudo apt-get install bridge-utils debootstrap expect \
        ifenslave  lsof lvm2  ntpdate libvirt-bin \
        tcpdump vlan aptitude build-essential \
        ntp ntpdate python-dev git figlet -y

grep -Rn virbr0.10 /etc/network/interfaces
if [ $? -ne 0 ]; then
  sudo  sh -c "cat $TEMPLATEI_PATH/bifrost/interfaces.temp >> /etc/network/interfaces"
  sudo ifdown -a && sudo ifup -a 
fi

ssh_args="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa"
IP_LIST="2 3 4 5 6"
for i in $IP_LIST
do
  MGMT_IP="192.168.122.$i"
  echo $MGMT_IP
  sudo ssh  $ssh_args root@$MGMT_IP apt-get install -y python
done
