#!/bin/bash
##############################################################################
# Copyright (c) 2015 Ericsson AB and others.
# jose.lausuch@ericsson.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

usage() {
    echo "usage: $0 [-v] -d <destination> -i <installer_type> -a <installer_ip> [-s <ssh_key>]" >&2
    echo "[-v] Virtualized deployment" >&2
    echo "[-s <ssh_key>] Path to ssh key. For MCP deployments only" >&2
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


swap_to_public() {
    if [ "$1" != "" ]; then
        info "Exchanging keystone public IP in rc file to $public_ip"
        sed -i  "/OS_AUTH_URL/c\export OS_AUTH_URL=\'$public_ip'" $dest_path
        sed -i 's/internalURL/publicURL/g' $dest_path
    fi
}


: ${DEPLOY_TYPE:=''}

#Get options
while getopts ":d:i:a:h:s:v" optchar; do
    case "${optchar}" in
        d) dest_path=${OPTARG} ;;
        i) installer_type=${OPTARG} ;;
        a) installer_ip=${OPTARG} ;;
        s) ssh_key=${OPTARG} ;;
        v) DEPLOY_TYPE="virt" ;;
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
if [ "${installer_type}" == "fuel" ] && [ "${BRANCH}" == "master" ]; then
    installer_ip=${SALT_MASTER_IP}
fi

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
    verify_connectivity $installer_ip
    if [ "${BRANCH}" == "master" ]; then
        ssh_key=${ssh_key:-$SSH_KEY}
        if [ -z $ssh_key ] || [ ! -f $ssh_key ]; then
            error "Please provide path to existing ssh key for mcp deployment."
            exit 2
        fi
        ssh_options+=" -i ${ssh_key}"

        # retrieving controller vip
        controller_ip=$(ssh 2>/dev/null ${ssh_options} ubuntu@${installer_ip} \
            "sudo salt --out txt 'ctl01*' pillar.get _param:openstack_control_address | awk '{print \$2}'" | \
            sed 's/ //g') &> /dev/null

        info "Fetching rc file from controller $controller_ip..."
        ssh ${ssh_options} ubuntu@${controller_ip} "sudo cat /root/keystonercv3" > $dest_path
    else
        #ip_fuel="10.20.0.2"
        env=$(sshpass -p r00tme ssh 2>/dev/null ${ssh_options} root@${installer_ip} \
            'fuel env'|grep operational|head -1|awk '{print $1}') &> /dev/null
        if [ -z $env ]; then
            error "No operational environment detected in Fuel"
        fi
        env_id="${FUEL_ENV:-$env}"

        # Check if controller is alive (online='True')
        controller_ip=$(sshpass -p r00tme ssh 2>/dev/null ${ssh_options} root@${installer_ip} \
            "fuel node --env ${env_id} | grep controller | grep 'True\|  1' | awk -F\| '{print \$5}' | head -1" | \
            sed 's/ //g') &> /dev/null

        if [ -z $controller_ip ]; then
            error "The controller $controller_ip is not up. Please check that the POD is correctly deployed."
        fi

        info "Fetching rc file from controller $controller_ip..."
        sshpass -p r00tme ssh 2>/dev/null ${ssh_options} root@${installer_ip} \
            "scp ${ssh_options} ${controller_ip}:/root/openrc ." &> /dev/null
        sshpass -p r00tme scp 2>/dev/null ${ssh_options} root@${installer_ip}:~/openrc $dest_path &> /dev/null
    fi
    #convert to v3 URL
    auth_url=$(cat $dest_path|grep AUTH_URL)
    if [[ -z `echo $auth_url |grep v3` ]]; then
        auth_url=$(echo $auth_url |sed "s|'$|v3&|")
    fi
    sed -i '/AUTH_URL/d' $dest_path
    echo $auth_url >> $dest_path

elif [ "$installer_type" == "apex" ]; then
    verify_connectivity $installer_ip

    # The credentials file is located in the Instack VM (192.0.2.1)
    # NOTE: This might change for bare metal deployments
    info "Fetching rc file from Instack VM $installer_ip..."
    if [ -f /root/.ssh/id_rsa ]; then
        chmod 600 /root/.ssh/id_rsa
    fi
    sudo scp $ssh_options root@$installer_ip:/home/stack/overcloudrc.v3 $dest_path

elif [ "$installer_type" == "compass" ]; then
    if [ "${BRANCH}" == "master" ]; then
        sudo docker cp compass-tasks:/opt/openrc $dest_path &> /dev/null
        sudo chown $(whoami):$(whoami) $dest_path
    else
        verify_connectivity $installer_ip
        controller_ip=$(sshpass -p'root' ssh 2>/dev/null $ssh_options root@${installer_ip} \
            'mysql -ucompass -pcompass -Dcompass -e"select *  from cluster;"' \
            | awk -F"," '{for(i=1;i<NF;i++)if($i~/\"127.0.0.1\"/) {print $(i+2);break;}}'  \
            | grep -oP "\d+.\d+.\d+.\d+")

        if [ -z $controller_ip ]; then
            error "The controller $controller_ip is not up. Please check that the POD is correctly deployed."
        fi

        info "Fetching rc file from controller $controller_ip..."
        sshpass -p root ssh 2>/dev/null $ssh_options root@${installer_ip} \
            "scp $ssh_options ${controller_ip}:/opt/admin-openrc.sh ." &> /dev/null
        sshpass -p root scp 2>/dev/null $ssh_options root@${installer_ip}:~/admin-openrc.sh $dest_path &> /dev/null

        info "This file contains the mgmt keystone API, we need the public one for our rc file"

        if grep "OS_AUTH_URL.*v2" $dest_path > /dev/null 2>&1 ; then
            public_ip=$(sshpass -p root ssh $ssh_options root@${installer_ip} \
                "ssh ${controller_ip} 'source /opt/admin-openrc.sh; openstack endpoint show identity '" \
                | grep publicurl | awk '{print $4}')
        else
            public_ip=$(sshpass -p root ssh $ssh_options root@${installer_ip} \
                "ssh ${controller_ip} 'source /opt/admin-openrc.sh; \
                     openstack endpoint list --interface public --service identity '" \
                | grep identity | awk '{print $14}')
        fi
        info "public_ip: $public_ip"
        swap_to_public $public_ip
    fi

elif [ "$installer_type" == "joid" ]; then
    # do nothing...for the moment
    # we can either do a scp from the jumphost or use the -v option to transmit the param to the docker file
    echo "Do nothing, creds will be provided through volume option at docker creation for joid"

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
    admin_ip=$(cat $dest_path | grep "OS_AUTH_URL" | sed 's/^.*\=//' | sed "s/^\([\"']\)\(.*\)\1\$/\2/g" | sed s'/\/$//')
    public_ip=$(sshpass -p vagrant ssh $ssh_options root@${installer_ip} \
        "sshpass -p Op3nStack ssh $ssh_options root@${controller} \
        'source keystonerc_admin;keystone endpoint-list'" \
        | grep $admin_ip | sed 's/ /\n/g' | grep ^http | head -1) &> /dev/null

elif [ "$installer_type" == "daisy" ]; then
    verify_connectivity $installer_ip
    cluster=$(sshpass -p r00tme ssh 2>/dev/null $ssh_options root@${installer_ip} \
            "source ~/daisyrc_admin; daisy cluster-list"|grep active|head -1|awk -F "|" '{print $3}') &> /dev/null
    if [ -z $cluster ]; then
        echo "No active cluster detected in daisy"
        exit 1
    fi

    sshpass -p r00tme scp 2>/dev/null $ssh_options root@${installer_ip}:/etc/kolla/admin-openrc.sh $dest_path &> /dev/null

else
    error "Installer $installer is not supported by this script"
fi


if [ ! -f $dest_path ]; then
    error "There has been an error retrieving the credentials"
fi

echo "-------- Credentials: --------"
cat $dest_path
