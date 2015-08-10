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
    logger -s -t "fetch_os_creds.info" "$*"
}


error () {
    logger -s -t "fetch_os_creds.error" "$*"
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

# set vars from env if not provided by user as options
dest_path=${dest_path:-$HOME/opnfv-openrc.sh}
installer_type=${installer_type:-$INSTALLER_TYPE}
installer_ip=${installer_ip:-$INSTALLER_IP}

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
        'fuel node | grep controller | grep True | awk "{print \$10}" | tail -1') &> /dev/null

    if [ -z $controller_ip ]; then
        error "The controller $controller_ip is not up. Please check that the POD is correctly deployed."
    fi

    info "Fetching rc file from controller $controller_ip..."
    sshpass -p r00tme ssh 2>/dev/null $ssh_options root@${installer_ip} \
        "scp $ssh_options ${controller_ip}:/root/openrc ." &> /dev/null
    sshpass -p r00tme scp 2>/dev/null $ssh_options root@${installer_ip}:~/openrc $dest_path &> /dev/null

    #This file contains the mgmt keystone API, we need the public one for our rc file
    admin_ip=$(cat $dest_path | grep "OS_AUTH_URL" | sed 's/^.*\=//' | sed "s/^\([\"']\)\(.*\)\1\$/\2/g" | sed s'/\/$//')
    public_ip=$(sshpass -p r00tme ssh $ssh_options root@${installer_ip} \
        "ssh ${controller_ip} 'source openrc; keystone endpoint-list'" \
        | grep $admin_ip | sed 's/ /\n/g' | grep ^http | head -1)
        #| grep http | head -1 | cut -d '|' -f 4 | sed 's/v1\/.*/v1\//' | sed 's/ //g') &> /dev/null
    #NOTE: this is super ugly sed 's/v1\/.*/v1\//'OS_AUTH_URL
    # but sometimes the output of endpoint-list is like this: http://172.30.9.70:8004/v1/%(tenant_id)s


elif [ "$installer_type" == "foreman" ]; then
    #ip_foreman="172.30.10.73"
    controller="oscontroller1.opnfv.com"
    verify_connectivity $installer_ip

    # Check if controller is alive (here is more difficult to get the ip from a command like "fuel node")
    sshpass -p vagrant ssh $ssh_options root@${installer_ip} \
        "sshpass -p Op3nStack ssh $ssh_options root@${controller} 'ls'" &> /dev/null
    if [ $? -ne 0 ]; then
        error "The controller ${controller} is not up. Please check that the POD is correctly deployed."
    fi

    info "Fetching openrc from a Foreman Controller '${controller}'..."
    sshpass -p vagrant ssh $ssh_options root@${installer_ip} \
        "sshpass -p Op3nStack scp $ssh_options root@${controller}:~/keystonerc_admin ." &> /dev/null
    sshpass -p vagrant scp $ssh_options root@${installer_ip}:~/keystonerc_admin $dest_path &> /dev/null

    #This file contains the mgmt keystone API, we need the public one for our rc file
    public_ip=$(sshpass -p vagrant ssh $ssh_options root@${installer_ip} \
        "sshpass -p Op3nStack ssh $ssh_options root@${controller} \
        'source keystonerc_admin;keystone endpoint-list'" \
        | grep http | head -1 | cut -d '|' -f 4 | sed 's/ //g') &> /dev/null

elif [ "$installer_type" == "compass" ]; then
    #ip_compass="10.1.0.12"
    verify_connectivity $installer_ip

    # Check if controller is alive (online='True')
    #controller_ip=$(sshpass -p root ssh 2>/dev/null $ssh_options root@${installer_ip} \
    #    'fuel node | grep controller | grep True | awk "{print \$10}" | tail -1') &> /dev/null
    # controller_ip='10.1.0.222'
    controller_ip=$(sshpass -p'root' ssh 2>/dev/null -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@10.1.0.12 \
        'mysql -ucompass -pcompass -Dcompass -e"select package_config  from cluster;"' \
        | awk -F"," '{for(i=1;i<NF;i++)if($i~/\"ha_proxy\": {\"vip\":/)print $i}' \
        | grep -oP "\d+.\d+.\d+.\d+")
    if [ -z $controller_ip ]; then
        error "The controller $controller_ip is not up. Please check that the POD is correctly deployed."
    fi

    info "Fetching rc file from controller $controller_ip..."
    sshpass -p root ssh 2>/dev/null $ssh_options root@${installer_ip} \
        "scp $ssh_options ${controller_ip}:/opt/admin-openrc.sh ." &> /dev/null
    sshpass -p root scp 2>/dev/null $ssh_options root@${installer_ip}:~/admin-openrc.sh $dest_path &> /dev/null
    echo 'export OS_REGION_NAME=regionOne' >> $dest_path

    info "This file contains the mgmt keystone API, we need the public one for our rc file"
    admin_ip=$(cat $dest_path | grep "OS_AUTH_URL" | sed 's/^.*\=//' | sed "s/^\([\"']\)\(.*\)\1\$/\2/g" | sed s'/\/$//')
    info "admin_ip: $admin_ip"
    public_ip=$(sshpass -p root ssh $ssh_options root@${installer_ip} \
        "ssh ${controller_ip} 'source /opt/admin-openrc.sh; keystone endpoint-list'" \
        | grep $admin_ip | sed 's/ /\n/g' | grep ^http | head -1)
        #| grep http | head -1 | cut -d '|' -f 4 | sed 's/v1\/.*/v1\//' | sed 's/ //g') &> /dev/null
    info "public_ip: $public_ip"
    #NOTE: this is super ugly sed 's/v1\/.*/v1\//'OS_AUTH_URL
    # but sometimes the output of endpoint-list is like this: http://172.30.9.70:8004/v1/%(tenant_id)s

else
    error "Installer $installer is not supported by this script"
fi



if [ "$public_ip" == "" ]; then
    error "Cannot retrieve the public IP from keystone"
fi

info "Keystone public IP is $public_ip"
sed -i  "/OS_AUTH_URL/c\export OS_AUTH_URL=\'$public_ip'" $dest_path

echo "-------- Credentials: --------"
cat $dest_path

exit 0
