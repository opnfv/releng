#!/bin/bash
set -e
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

rc_file_vol=""
cacert_file_vol=""
sshkey=""

rc_file_vol="-v ${HOME}/opnfv-openrc.sh:/etc/yardstick/openstack.creds"

if [[ ${INSTALLER_TYPE} == 'apex' ]]; then
    instack_mac=$(sudo virsh domiflist undercloud | grep default | \
                  grep -Eo "[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+")
    INSTALLER_IP=$(/usr/sbin/arp -e | grep ${instack_mac} | awk {'print $1'})
    sshkey="-v /root/.ssh/id_rsa:/root/.ssh/id_rsa"
    if [[ -n $(sudo iptables -L FORWARD |grep "REJECT"|grep "reject-with icmp-port-unreachable") ]]; then
        #note: this happens only in opnfv-lf-pod1
        sudo iptables -D FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable
        sudo iptables -D FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable
    fi
fi

if [[ ${INSTALLER_TYPE} == 'joid' ]]; then
    if [[ "${DEPLOY_SCENARIO:0:2}" == "k8" ]];then
        rc_file_vol="-v ${HOME}/admin.conf:/etc/yardstick/admin.conf"
    else
        # If production lab then creds may be retrieved dynamically
        # creds are on the jumphost, always in the same folder
        rc_file_vol="-v $LAB_CONFIG/admin-openrc:/etc/yardstick/openstack.creds"
        # If dev lab, credentials may not be the default ones, just provide a path to put them into docker
        # replace the default one by the customized one provided by jenkins config
    fi
elif [[ ${INSTALLER_TYPE} == 'compass' ]]; then
    if [[ "${DEPLOY_SCENARIO:0:2}" == "k8" ]];then
        rc_file_vol="-v ${HOME}/admin.conf:/etc/yardstick/admin.conf"
    else
        cacert_file_vol="-v ${HOME}/os_cacert:/etc/yardstick/os_cacert"
        echo "export OS_CACERT=/etc/yardstick/os_cacert" >> ${HOME}/opnfv-openrc.sh
    fi
elif [[ ${INSTALLER_TYPE} == 'fuel' ]]; then
    cacert_file_vol="-v ${HOME}/os_cacert:/etc/ssl/certs/mcp_os_cacert"
    sshkey="-v ${SSH_KEY}:/root/.ssh/mcp.rsa"
fi
# Set iptables rule to allow forwarding return traffic for container
if ! sudo iptables -C FORWARD -j RETURN 2> ${redirect} || ! sudo iptables -L FORWARD | awk 'NR==3' | grep RETURN 2> ${redirect}; then
    sudo iptables -I FORWARD -j RETURN
fi

opts="--privileged=true --rm"
envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP} \
    -e NODE_NAME=${NODE_NAME} -e EXTERNAL_NETWORK=${EXTERNAL_NETWORK} \
    -e YARDSTICK_BRANCH=${BRANCH} -e BRANCH=${BRANCH} \
    -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} -e CI_DEBUG=true"

if [[ "${INSTALLER_TYPE}" == 'fuel' ]]; then
    envs+=" -e SSH_KEY=/root/.ssh/mcp.rsa"
fi

# Pull the image with correct tag
DOCKER_REPO='opnfv/yardstick'
if [ "$(uname -m)" = 'aarch64' ]; then
    DOCKER_REPO="${DOCKER_REPO}_$(uname -m)"
fi
echo "Yardstick: Pulling image ${DOCKER_REPO}:${DOCKER_TAG}"
docker pull ${DOCKER_REPO}:$DOCKER_TAG >$redirect
docker images

# map log directory
branch=${BRANCH##*/}
dir_result="${HOME}/opnfv/yardstick/results/${branch}"
mkdir -p ${dir_result}
sudo rm -rf ${dir_result}/*
map_log_dir="-v ${dir_result}:/tmp/yardstick"

# Run docker
cmd="sudo docker run ${opts} ${envs} ${rc_file_vol} ${cacert_file_vol} ${map_log_dir} ${sshkey} ${DOCKER_REPO}:${DOCKER_TAG} \
exec_tests.sh ${YARDSTICK_DB_BACKEND} ${YARDSTICK_SCENARIO_SUITE_NAME}"

echo "Yardstick: Running docker cmd: ${cmd}"
${cmd}

echo "Yardstick: done!"
