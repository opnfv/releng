#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

if [ -z ${RC_FILE_PATH+x} ]; then
  undercloud_mac=$(sudo virsh domiflist undercloud | grep default | \
                   grep -Eo "[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+")
  INSTALLER_IP=$(/usr/sbin/arp -e | grep ${undercloud_mac} | awk {'print $1'})
  sudo scp -o StrictHostKeyChecking=no root@$INSTALLER_IP:/home/stack/overcloudrc /tmp/overcloudrc
else
  cp -f $RC_FILE_PATH ${WORKSPACE}/overcloudrc
fi

sudo chmod 755 ${WORKSPACE}/overcloudrc
source ${WORKSPACE}/overcloudrc

# copy ssh key for robot

if [ -z ${SSH_KEY_PATH+x} ]; then
  sudo scp -o StrictHostKeyChecking=no root@$INSTALLER_IP:/home/stack/.ssh/id_rsa ${WORKSPACE}/
  sudo chown -R jenkins-ci:jenkins-ci ${WORKSPACE}/
  # done with sudo. jenkins-ci is the user from this point
  chmod 0600 ${WORKSPACE}/id_rsa
else
  cp -f ${SSH_KEY_PATH} ${WORKSPACE}/
fi

docker pull opnfv/cperf:$DOCKER_TAG

sudo mkdir -p /tmp/robot_results
