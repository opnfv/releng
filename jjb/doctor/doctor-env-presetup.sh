#!/usr/bin/env bash
set -o errexit
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
        echo "Installer ip is ${INSTALLER_IP}"
    else
        echo "No available installer VM exists and no credentials provided...exiting"
        exit 1
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
fi

