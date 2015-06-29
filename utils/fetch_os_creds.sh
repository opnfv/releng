#!/bin/bash
##############################################################################
# Copyright (c) 2015 Ericsson AB and others.
# jose.lausuch@ericsson.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


usage() {
    echo "usage: $0 -d <destination> -i <installer_type> -a <installer_ip>" >&2
}

info ()  {
    logger -s -t "retrieve_rc.info" "$*"
}


error () {
    logger -s -t "retrieve_rc.error" "$*"
    exit 1
}


verify_connectivity() {
    local ip=$1
    info "Verifying connectivity to $ip..."
    for i in $(seq 0 10); do
        if ping -c 1 -W 1 $ip > /dev/null; then
            info "$ip is reachable!"
            return 0
        fi
        sleep 1
    done
    error "Can not talk to $ip."
}



#Get options
while getopts ":d:i:a:h:" optchar; do
    case "${optchar}" in
        d) dest_path=${OPTARG} ;;
        i) installer_type=${OPTARG} ;;
        a) installer_ip=${OPTARG} ;;
        *) echo "Non-option argument: '-${OPTARG}'" >&2
           usage
           exit 2
           ;;
    esac
done

if [ -z $dest_path ] || [ -z $installer_type ] || [ -z $installer_ip ]; then
    usage
    exit 2
fi


# Checking if destination path is valid
if [ -d $dest_path ]; then
    error "Please provide the full destination path for the credentials file including the filename"
else
    # Check if we can create the file (e.g. path is correct)
    touch $dest_path || error "Cannot create the file specified. Check that the path is correct and run the script again."
fi


ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

# Start fetching the files
if [ "$installer_type" == "fuel" ]; then
    #ip_fuel="10.20.0.2"
    verify_connectivity $installer_ip

    # Check if controller is alive (online='True')
    controller_ip=$(sshpass -p r00tme ssh 2>/dev/null $ssh_options root@${installer_ip} \
        'fuel node | grep controller | grep True | awk "{print \$10}" | tail -1')

    if [ -z $controller_ip ]; then
        error "The controller $controller_ip is not up. Please check that the POD is correctly deployed."
    fi

    info "Fetching rc file from controller $controller_ip..."
    sshpass -p r00tme ssh 2>/dev/null $ssh_options root@${installer_ip} 'scp ${controller_ip}:/root/openrc .'
    sshpass -p r00tme scp 2>/dev/null $ssh_options root@${installer_ip}:~/openrc $dest_path

    #This file contains the mgmt keystone API, we need the public one for our rc file
    public_ip=$(sshpass -p r00tme ssh $ssh_options root@${installer_ip} \
        'ssh ${controller_ip} "source openrc; keystone endpoint-list"' | grep http | head -1 | cut -d '|' -f 4 | sed 's/\([0-9]\):[0-9]*.*/\1/' | sed 's/ //g')


elif [ "$installer" == "foreman" ]; then
    #ip_foreman="172.30.10.73"

    verify_connectivity $installer_ip

    # Check if controller is alive (here is more difficult to get the ip from a command like "fuel node")
    sshpass -p vagrant ssh $ssh_options root@${installer_ip} 'sshpass -p Op3nStack ssh $ssh_options root@oscontroller1.opnfv.com "ls"'
    if [ $? -ne 0 ]; then
        error "The controller oscontroller1.opnfv.com is not up. Please check that the POD is correctly deployed."
    fi

    info "Fetching openrc from a Foreman Controller 'oscontroller1.opnfv.com'..."
    sshpass -p vagrant ssh $ssh_options root@${installer_ip} 'sshpass -p Op3nStack scp $ssh_options root@oscontroller1.opnfv.com:~/keystonerc_admin .'
    sshpass -p vagrant scp $ssh_options root@${installer_ip}:~/keystonerc_admin $dest_path

    #This file contains the mgmt keystone API, we need the public one for our rc file
    public_ip=$(sshpass -p vagrant ssh $ssh_options root@${installer_ip} 'sshpass -p Op3nStack ssh $ssh_options root@oscontroller1.opnfv.com \
        "source keystonerc_admin;keystone endpoint-list"' | grep http | head -1 | cut -d '|' -f 4 | sed 's/ //g')

else
    error "Installer $installer is not supported by this script"
fi



if [ "$public_ip" == "" ]; then
    error "Cannot retrieve the public IP from keystone"
fi

info "Keystone public IP is $public_ip"
sed -i  "/OS_AUTH_URL/c\export OS_AUTH_URL=\'$public_ip'" $dest_path
cat $dest_path

exit 0
