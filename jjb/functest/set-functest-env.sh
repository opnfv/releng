#!/bin/bash

set -e
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"
# LAB_CONFIG is used only for joid


if [[ ${INSTALLER_TYPE} == 'joid' ]]; then
    # If production lab then creds may be retrieved dynamically
    # creds are on the jumphost, always in the same folder
    rc_file_vol="-v $LAB_CONFIG/admin-openrc:/home/opnfv/functest/conf/openstack.creds"
    # If dev lab, credentials may not be the default ones, just provide a path to put them into docker
    # replace the default one by the customized one provided by jenkins config
fi

if [[ ${RC_FILE_PATH} != '' ]] && [[ -f ${RC_FILE_PATH} ]] ; then
    echo "Credentials file detected: ${RC_FILE_PATH}"
    # volume if credentials file path is given to Functest
    rc_file_vol="-v ${RC_FILE_PATH}:/home/opnfv/functest/conf/openstack.creds"
    RC_FLAG=1
fi


if [[ ${INSTALLER_TYPE} == 'apex' ]]; then
    ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    if sudo virsh list | grep undercloud; then
        echo "Installer VM detected"
        undercloud_mac=$(sudo virsh domiflist undercloud | grep default | \
                      grep -Eo "[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+")
        INSTALLER_IP=$(/usr/sbin/arp -e | grep ${undercloud_mac} | awk {'print $1'})
        sshkey_vol="-v /root/.ssh/id_rsa:/root/.ssh/id_rsa"
        sudo scp $ssh_options root@${INSTALLER_IP}:/home/stack/stackrc ${HOME}/stackrc
        stackrc_vol="-v ${HOME}/stackrc:/home/opnfv/functest/conf/stackrc"

        if sudo iptables -C FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable 2> ${redirect}; then
            sudo iptables -D FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable
        fi
        if sudo iptables -C FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable 2> ${redirect}; then
          sudo iptables -D FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable
        fi
    elif [[ "$RC_FLAG" == 1 ]]; then
        echo "No available installer VM, but credentials provided...continuing"
    else
        echo "No available installer VM exists and no credentials provided...exiting"
        exit 1
    fi

fi



# Set iptables rule to allow forwarding return traffic for container
if ! sudo iptables -C FORWARD -j RETURN 2> ${redirect} || ! sudo iptables -L FORWARD | awk 'NR==3' | grep RETURN 2> ${redirect}; then
    sudo iptables -I FORWARD -j RETURN
fi

DEPLOY_TYPE=baremetal
[[ $BUILD_TAG =~ "virtual" ]] && DEPLOY_TYPE=virt

echo "Functest: Start Docker and prepare environment"

dir_result="${HOME}/opnfv/functest/results/${BRANCH##*/}"
mkdir -p ${dir_result}
sudo rm -rf ${dir_result}/*
results_vol="-v ${dir_result}:/home/opnfv/functest/results"
custom_params=
test -f ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG} && custom_params=$(cat ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG})

envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP} \
    -e NODE_NAME=${NODE_NAME} -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
    -e BUILD_TAG=${BUILD_TAG} -e CI_DEBUG=${CI_DEBUG} -e DEPLOY_TYPE=${DEPLOY_TYPE}"

if [[ ${INSTALLER_TYPE} == 'compass' && ${DEPLOY_SCENARIO} == *'os-nosdn-openo-ha'* ]]; then
    ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    openo_msb_port=${openo_msb_port:-80}
    openo_msb_endpoint="$(sshpass -p'root' ssh 2>/dev/null $ssh_options root@${installer_ip} \
    'mysql -ucompass -pcompass -Dcompass -e "select package_config from cluster;" \
    | sed s/,/\\n/g | grep openo_ip | cut -d \" -f 4'):$openo_msb_port"

    envs=${env}" -e OPENO_MSB_ENDPOINT=${openo_msb_endpoint}"
fi

volumes="${results_vol} ${sshkey_vol} ${stackrc_vol} ${rc_file_vol}"

HOST_ARCH=$(uname -m)
FUNCTEST_IMAGE="opnfv/functest"
if [ "$HOST_ARCH" = "aarch64" ]; then
    FUNCTEST_IMAGE="${FUNCTEST_IMAGE}_${HOST_ARCH}"
fi

echo "Functest: Pulling image ${FUNCTEST_IMAGE}:${DOCKER_TAG}"
docker pull ${FUNCTEST_IMAGE}:$DOCKER_TAG >/dev/null

cmd="sudo docker run --privileged=true -id ${envs} ${volumes} \
     ${custom_params} ${TESTCASE_OPTIONS} \
     ${FUNCTEST_IMAGE}:${DOCKER_TAG} /bin/bash"
echo "Functest: Running docker run command: ${cmd}"
${cmd} >${redirect}
sleep 5
container_id=$(docker ps | grep "${FUNCTEST_IMAGE}:${DOCKER_TAG}" | awk '{print $1}' | head -1)
echo "Container ID=${container_id}"
if [ -z ${container_id} ]; then
    echo "Cannot find opnfv/functest container ID ${container_id}. Please check if it is existing."
    docker ps -a
    exit 1
fi
echo "Starting the container: docker start ${container_id}"
docker start ${container_id}
sleep 5
docker ps >${redirect}
if [ $(docker ps | grep "${FUNCTEST_IMAGE}:${DOCKER_TAG}" | wc -l) == 0 ]; then
    echo "The container ${FUNCTEST_IMAGE} with ID=${container_id} has not been properly started. Exiting..."
    exit 1
fi

cmd="python ${FUNCTEST_REPO_DIR}/functest/ci/prepare_env.py start"

echo "Executing command inside the docker: ${cmd}"
docker exec ${container_id} ${cmd}
