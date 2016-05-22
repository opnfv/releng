#!/bin/bash

set -e
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"
# labconfig is used only for joid
labconfig=""
if [[ ${INSTALLER_TYPE} == 'apex' ]]; then
    if sudo virsh list | grep instack; then
        instack_mac=$(sudo virsh domiflist instack | grep default | \
                      grep -Eo "[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+")
    elif sudo virsh list | grep undercloud; then
        instack_mac=$(sudo virsh domiflist undercloud | grep default | \
                      grep -Eo "[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+")
    else
        echo "No available installer VM exists...exiting"
        exit 1
    fi
    INSTALLER_IP=$(/usr/sbin/arp -e | grep ${instack_mac} | awk {'print $1'})
    sshkey="-v /root/.ssh/id_rsa:/root/.ssh/id_rsa"
    if sudo iptables -C FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable 2> ${redirect}; then
        sudo iptables -D FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable
    fi
    if sudo iptables -C FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable 2> ${redirect}; then
        sudo iptables -D FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable
    fi
elif [[ ${INSTALLER_TYPE} == 'joid' ]]; then
    # If production lab then creds may be retrieved dynamically
    # creds are on the jumphost, always in the same folder
    labconfig="-v $LAB_CONFIG/admin-openrc:/home/opnfv/functest/conf/openstack.creds"
    # If dev lab, credentials may not be the default ones, just provide a path to put them into docker
    # replace the default one by the customized one provided by jenkins config
fi
echo "Functest: Start Docker and prepare environment"
envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP} \
    -e NODE_NAME=${NODE_NAME} -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
    -e BUILD_TAG=${BUILD_TAG} -e CI_DEBUG=${CI_DEBUG}"
branch=${GIT_BRANCH##*/}
dir_result="${HOME}/opnfv/functest/results/${branch}"
mkdir -p ${dir_result}
sudo rm -rf ${dir_result}/*
res_volume="-v ${dir_result}:/home/opnfv/functest/results"
custom_params=
test -f ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG} && custom_params=$(cat ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG})

echo "Functest: Pulling image opnfv/functest:${DOCKER_TAG}"
docker pull opnfv/functest:$DOCKER_TAG >/dev/null

cmd="sudo docker run --privileged=true -id ${envs} ${labconfig} ${sshkey} ${res_volume} ${custom_params} opnfv/functest:${DOCKER_TAG} /bin/bash"
echo "Functest: Running docker run command: ${cmd}"
${cmd} >${redirect}
sleep 5
container_id=$(docker ps | grep "opnfv/functest:${DOCKER_TAG}" | awk '{print $1}' | head -1)
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
if [ $(docker ps | grep "opnfv/functest:${DOCKER_TAG}" | wc -l) == 0 ]; then
    echo "The container opnfv/functest with ID=${container_id} has not been properly started. Exiting..."
    exit 1
fi
if [[ ${branch} == *"brahmaputra"* ]]; then
    cmd="${FUNCTEST_REPO_DIR}/docker/prepare_env.sh"
else
    cmd="python ${FUNCTEST_REPO_DIR}/ci/prepare_env.py start"
fi
echo "Executing command inside the docker: ${cmd}"
docker exec ${container_id} ${cmd}
