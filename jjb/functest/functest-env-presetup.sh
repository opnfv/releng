#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# Fetch INSTALLER_IP for APEX deployments
if [[ ${INSTALLER_TYPE} == 'apex' ]]; then
    if [ ! -z ${RC_FILE_PATH+x} ]; then
        echo "RC_FILE_PATH is set: ${RC_FILE_PATH}...skipping detecting UC IP"
    else
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

elif [[ ${INSTALLER_TYPE} == 'daisy' ]]; then
    echo "Gathering IP information for Daisy installer VM"
    if sudo virsh list | grep daisy; then
        echo "Installer VM detected"

        bridge_name=$(sudo virsh domiflist daisy | grep vnet | awk '{print $3}')
        echo "Bridge is $bridge_name"

        installer_mac=$(sudo virsh domiflist daisy | grep vnet | \
                      grep -Eo "[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+")
        export INSTALLER_IP=$(/usr/sbin/arp -e -i $bridge_name | grep ${installer_mac} | head -n 1 | awk {'print $1'})

        echo "Installer ip is ${INSTALLER_IP}"
    else
        echo "No available installer VM exists...exiting"
        exit 1
    fi

elif [[ ${INSTALLER_TYPE} == 'fuel' ]]; then
    if [[ ! "${BRANCH}" =~ "danube" ]]; then
        echo "Map mcp ssh_key"
        export sshkey_vol="-v ${SSH_KEY:-/var/lib/opnfv/mcp.rsa}:/root/.ssh/id_rsa"
    fi
fi

