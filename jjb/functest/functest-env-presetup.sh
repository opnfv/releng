#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# Fetch INSTALLER_IP for APEX deployments
if [[ ${INSTALLER_TYPE} == 'apex' ]]; then
    echo "Gathering IP information for Apex installer VM"
    ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    if sudo virsh list | grep undercloud; then
        echo "Installer VM detected"
        undercloud_mac=$(sudo virsh domiflist undercloud | grep default | \
                      grep -Eo "[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+")
        export INSTALLER_IP=$(/usr/sbin/arp -e | grep ${undercloud_mac} | awk {'print $1'})
        export sshkey_vol="-v /root/.ssh/id_rsa:/root/.ssh/id_rsa"
        sudo scp $ssh_options root@${INSTALLER_IP}:/home/stack/stackrc ${HOME}/stackrc
        export stackrc_vol="-v ${HOME}/stackrc:/home/opnfv/functest/conf/stackrc"

        if sudo iptables -C FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable 2> ${redirect}; then
            sudo iptables -D FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable
        fi
        if sudo iptables -C FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable 2> ${redirect}; then
          sudo iptables -D FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable
        fi
        echo "Installer ip is ${INSTALLER_IP}"
    else
        echo "No available installer VM exists and no credentials provided...exiting"
        exit 1
    fi
fi

