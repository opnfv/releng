#!/usr/bin/env bash
set -o errexit
set -o pipefail

# set vars from env if not provided by user as options
installer_key_file=${installer_key_file:-$HOME/installer_key_file}
opnfv_installer=${opnfv_installer:-$HOME/opnfv-installer.sh}

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

    sudo cp /root/.ssh/id_rsa ${installer_key_file}
    sudo chown `whoami`:`whoami` ${installer_key_file}

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


# Checking if destination path is valid
if [ -d $opnfv_installer ]; then
    error "Please provide the full destination path for the installer ip file including the filename"
else
    # Check if we can create the file (e.g. path is correct)
    touch $opnfv_installer || error "Cannot create the file specified. Check that the path is correct and run the script again."
fi


# Write the installer info to the file
echo export INSTALLER_TYPE=${INSTALLER_TYPE} > $opnfv_installer
echo export INSTALLER_IP=${INSTALLER_IP} >> $opnfv_installer
if [ -e ${installer_key_file ]; then
    echo export SSH_KEY=${installer_key_file} >> $opnfv_installer
fi
