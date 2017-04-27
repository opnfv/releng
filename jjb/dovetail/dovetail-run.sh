#!/bin/bash

#the noun INSTALLER is used in community, here is just the example to run.
#multi-platforms are supported.

set -e
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

sshkey=""
# The path of openrc.sh is defined in fetch_os_creds.sh
OPENRC=$WORKSPACE/opnfv-openrc.sh
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
    sudo cp $LAB_CONFIG/admin-openrc $OPENRC
    # If dev lab, credentials may not be the default ones, just provide a path to put them into docker
    # replace the default one by the customized one provided by jenkins config
fi

# Set iptables rule to allow forwarding return traffic for container
if ! sudo iptables -C FORWARD -j RETURN 2> ${redirect} || ! sudo iptables -L FORWARD | awk 'NR==3' | grep RETURN 2> ${redirect}; then
    sudo iptables -I FORWARD -j RETURN
fi

releng_repo=${WORKSPACE}/releng
[ -d ${releng_repo} ] && sudo rm -rf ${releng_repo}
git clone https://gerrit.opnfv.org/gerrit/releng ${releng_repo} >/dev/null

if [[ ${INSTALLER_TYPE} != 'joid' ]]; then
    ${releng_repo}/utils/fetch_os_creds.sh -d ${OPENRC} -i ${INSTALLER_TYPE} -a ${INSTALLER_IP} >${redirect}
fi

if [[ -f $OPENRC ]]; then
    echo "INFO: openstack credentials path is $OPENRC"
    cat $OPENRC
else
    echo "ERROR: file $OPENRC does not exist."
    exit 1
fi

pip install virtualenv

cd ${releng_repo}/modules
virtualenv venv
source venv/bin/activate
sudo pip install -e ./ >/dev/null

if [[ ${INSTALLER_TYPE} == apex ]]; then
    options="-u stack -k /root/.ssh/id_rsa"
elif [[ ${INSTALLER_TYPE} == compass ]]; then
    options="-u root -p root"
elif [[ ${INSTALLER_TYPE} == fuel ]]; then
    options="-u root -p r00tme"
else
    echo "Don't support to generate pod.yaml on ${INSTALLER_TYPE} currently."
    echo "HA test cases may not run properly."
fi

pod_file_dir="/home/opnfv/dovetail/userconfig"
cmd="sudo python ${releng_repo}/utils/create_pod_file.py -t ${INSTALLER_TYPE} -i ${INSTALLER_IP} ${options} -f ${pod_file_dir}/pod.yaml"
echo ${cmd}
${cmd}

deactivate

if [ -f ${pod_file_dir}/pod.yaml ]; then
    echo "file ${pod_file_dir}/pod.yaml:"
    cat ${pod_file_dir}/pod.yaml
else
    echo "Error: There doesn't exist file ${pod_file_dir}/pod.yaml."
    echo "HA test cases may not run properly."
fi

opts="--privileged=true -id"
results_envs="-v /var/run/docker.sock:/var/run/docker.sock \
              -v /home/opnfv/dovetail/results:/home/opnfv/dovetail/results"
openrc_volume="-v ${OPENRC}:${OPENRC}"
userconfig_volume="-v ${pod_file_dir}:${pod_file_dir}"

# Pull the image with correct tag
echo "Dovetail: Pulling image opnfv/dovetail:${DOCKER_TAG}"
docker pull opnfv/dovetail:$DOCKER_TAG >$redirect

cmd="docker run ${opts} ${results_envs} ${openrc_volume} ${userconfig_volume} \
     ${sshkey} opnfv/dovetail:${DOCKER_TAG} /bin/bash"
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
run_cmd="dovetail run --openrc ${OPENRC} --testsuite ${TESTSUITE} -d"
echo "Container exec command: ${list_cmd}"
docker exec $container_id ${list_cmd}
echo "Container exec command: ${run_cmd}"
docker exec $container_id ${run_cmd}

sudo cp -r ${DOVETAIL_REPO_DIR}/results ./
# To make sure the file owner is the current user, for the copied results files in the above line
# if not, there will be error when next time to wipe workspace
# CURRENT_USER=${SUDO_USER:-$USER}
# PRIMARY_GROUP=$(id -gn $CURRENT_USER)
# sudo chown -R ${CURRENT_USER}:${PRIMARY_GROUP} ${WORKSPACE}/results

echo "Dovetail: done!"

