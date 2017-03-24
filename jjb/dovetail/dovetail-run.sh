#!/bin/bash

#the noun INSTALLER is used in community, here is just the example to run.
#multi-platforms are supported.

set -e
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

# labconfig is used only for joid
labconfig=""
sshkey=""
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
elif [[ ${INSTALLER_TYPE} == 'joid' ]]; then
    # If production lab then creds may be retrieved dynamically
    # creds are on the jumphost, always in the same folder
    labconfig="-v $LAB_CONFIG/admin-openrc:/home/opnfv/functest/conf/openstack.creds"
    # If dev lab, credentials may not be the default ones, just provide a path to put them into docker
    # replace the default one by the customized one provided by jenkins config
fi

# Set iptables rule to allow forwarding return traffic for container
if ! sudo iptables -C FORWARD -j RETURN 2> ${redirect} || ! sudo iptables -L FORWARD | awk 'NR==3' | grep RETURN 2> ${redirect}; then
    sudo iptables -I FORWARD -j RETURN
fi

opts="--privileged=true -id"
envs="-e CI_DEBUG=${CI_DEBUG} \
      -e INSTALLER_TYPE=${INSTALLER_TYPE} \
      -e INSTALLER_IP=${INSTALLER_IP} \
      -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
      -e DEPLOY_TYPE=${DEPLOY_TYPE}"
results_envs="-v /var/run/docker.sock:/var/run/docker.sock \
              -v /home/opnfv/dovetail/results:/home/opnfv/dovetail/results"

# Pull the image with correct tag
echo "Dovetail: Pulling image opnfv/dovetail:${DOCKER_TAG}"
docker pull opnfv/dovetail:$DOCKER_TAG >$redirect

cmd="sudo docker run ${opts} ${envs} ${results_envs} ${labconfig} ${sshkey} \
     opnfv/dovetail:${DOCKER_TAG} /bin/bash"
echo "Dovetail: running docker run command: ${cmd}"
${cmd} >${redirect}
sleep 5
container_id=$(docker ps | grep "opnfv/dovetail:${DOCKER_TAG}" | awk '{print $1}' | head -1)
echo "Container ID=${container_id}"
if [ -z ${container_id} ]; then
    echo "Cannot find opnfv/dovetail container ID ${container_id}. Please check if it is existing."
    docker ps -a
    exit 1
fi
echo "Container Start: docker start ${container_id}"
docker start ${container_id}
sleep 5
docker ps >${redirect}
if [ $(docker ps | grep "opnfv/dovetail:${DOCKER_TAG}" | wc -l) == 0 ]; then
    echo "The container opnfv/dovetail with ID=${container_id} has not been properly started. Exiting..."
    exit 1
fi

list_cmd="dovetail list ${TESTSUITE}"
run_cmd="dovetail run --testsuite ${TESTSUITE} -d true"
echo "Container exec command: ${list_cmd}"
docker exec $container_id ${list_cmd}
echo "Container exec command: ${run_cmd}"
docker exec $container_id ${run_cmd}

sudo cp -r ${DOVETAIL_REPO_DIR}/results ./
#To make sure the file owner is jenkins, for the copied results files in the above line
#if not, there will be error when next time to wipe workspace
CURRENT_USER=${SUDO_USER:-$USER}
PRIMARY_GROUP=$(id -gn $CURRENT_USER)
sudo chown -R ${CURRENT_USER}:${PRIMARY_GROUP} ${WORKSPACE}/results

echo "Dovetail: done!"
