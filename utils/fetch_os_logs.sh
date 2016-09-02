#!/bin/bash
# Maintainer> jose.lausuch@ericsson.com

usage() {
    echo "usage: $0 [-v] -d <destination> -i <installer_type> -a <installer_ip>" >&2
    echo "[-v] Virtualized deployment" >&2
}

info ()  {
    logger -s -t "fetch_os_logs.info" "$*"
}


error () {
    logger -s -t "fetch_os_logs.error" "$*"
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

: ${DEPLOY_TYPE:=''}

#Get options
while getopts ":d:i:a:h:v" optchar; do
    case "${optchar}" in
        d) dest_path=${OPTARG} ;;
        i) installer_type=${OPTARG} ;;
        a) installer_ip=${OPTARG} ;;
        v) DEPLOY_TYPE="virt" ;;
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
    error "${dest_path} is not a directory."
fi


ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

# Start fetching the files
if [ "$installer_type" == "fuel" ]; then
    #ip_fuel="10.20.0.2"
    verify_connectivity $installer_ip

    env=$(sshpass -p r00tme ssh 2>/dev/null $ssh_options root@${installer_ip} \
        'fuel env'|grep operational|head -1|awk '{print $1}') &> /dev/null
    if [ -z $env ]; then
        error "No operational environment detected in Fuel"
    fi
    env_id="${FUEL_ENV:-$env}"
    
    #Let fuel collect the logs from the nodes
    sshpass -p r00tme ssh 2>/dev/null $ssh_options root@${installer_ip} \
        'fuel snapshot' &> /dev/null || error "Cannot run fuel snapshot."
    
    scp $ssh_options root@10.20.0.2:/root/fuel-snapshot* $dest_path || \
        error "Cannot scp the logs from fuel."

elif [ "$installer_type" == "apex" ]; then
    verify_connectivity $installer_ip
    nodes=($(opnfv-util undercloud stack "source stackrc; nova list" | \
        grep overcloud|awk '{print $4}'))
    for node in ${nodes[@]}; do
        node=$node|sed 's/overcloud\-//'
        opnfv-util overcloud $node "sudo tar cvzf -r ${node}_logs.zip /var/log/" \
            || error "Cannot fetch logs from node ${node}"
        scp heat-admin@${installer_ip}:${node}_logs.tar.gz $dest_path \
            || error "Cannot scp logs from undercloud."
    done

elif [ "$installer_type" == "compass" ]; then
    error "Not supported yet."

elif [ "$installer_type" == "joid" ]; then
   error "Not supported yet."

else
    error "Installer $installer is not supported by this script"
fi


if [ ! -f $dest_path ]; then
    error "There has been an error fetching the logs."
fi

echo "Deployment logs in ${dest_path}" 

exit 0
