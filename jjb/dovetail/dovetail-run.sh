#!/bin/bash
##############################################################################
# Copyright (c) 2017 Huawei Technologies Co.,Ltd and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

#the noun INSTALLER is used in community, here is just the example to run.
#multi-platforms are supported.

set -e
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

DEPLOY_TYPE=baremetal
[[ $BUILD_TAG =~ "virtual" ]] && DEPLOY_TYPE=virt

DOVETAIL_HOME=${WORKSPACE}/cvp
[ -d ${DOVETAIL_HOME} ] && sudo rm -rf ${DOVETAIL_HOME}

mkdir -p ${DOVETAIL_HOME}

DOVETAIL_CONFIG=${DOVETAIL_HOME}/pre_config
mkdir -p ${DOVETAIL_CONFIG}

DOVETAIL_IMAGES=${DOVETAIL_HOME}/images
mkdir -p ${DOVETAIL_IMAGES}

ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

sshkey=""
# The path of openrc.sh is defined in fetch_os_creds.sh
OPENRC=${DOVETAIL_CONFIG}/env_config.sh
CACERT=${DOVETAIL_CONFIG}/os_cacert
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
    echo "SUT branch is $SUT_BRANCH"
    echo "dovetail branch is $BRANCH"
    BRANCH_BACKUP=$BRANCH
    export BRANCH=$SUT_BRANCH
    ${releng_repo}/utils/fetch_os_creds.sh -d ${OPENRC} -i ${INSTALLER_TYPE} -a ${INSTALLER_IP} -o ${CACERT} >${redirect}
    export BRANCH=$BRANCH_BACKUP
fi

if [[ -f $OPENRC ]]; then
    echo "INFO: openstack credentials path is $OPENRC"
    if [[ ! "${SUT_BRANCH}" =~ "danube" && ${INSTALLER_TYPE} == "compass" ]]; then
        if [[ -f ${CACERT} ]]; then
            echo "INFO: ${INSTALLER_TYPE} openstack cacert file is ${CACERT}"
            echo "export OS_CACERT=${CACERT}" >> ${OPENRC}
        else
            echo "ERROR: Can't find ${INSTALLER_TYPE} openstack cacert file. Please check if it is existing."
            sudo ls -al ${DOVETAIL_CONFIG}
            exit 1
        fi
    fi
else
    echo "ERROR: cannot find file $OPENRC. Please check if it is existing."
    sudo ls -al ${DOVETAIL_CONFIG}
    exit 1
fi

if [[ ! "${SUT_BRANCH}" =~ "danube" && ${INSTALLER_TYPE} == "fuel" ]]; then
    sed -i "s#/etc/ssl/certs/mcp_os_cacert#${CACERT}#g" ${OPENRC}
fi
cat $OPENRC

if [[ ! "${SUT_BRANCH}" =~ "danube" && ${INSTALLER_TYPE} == "compass" ]]; then
    compass_repo=${WORKSPACE}/compass4nfv/
    git clone https://github.com/opnfv/compass4nfv.git ${compass_repo} >/dev/null
    sudo pip install shyaml
    scenario_file=${compass_repo}/deploy/conf/hardware_environment/$NODE_NAME/os-nosdn-nofeature-ha.yml
    ipmiIp=$(cat ${scenario_file} | shyaml get-value hosts.0.ipmiIp)
    ipmiPass=$(cat ${scenario_file} | shyaml get-value hosts.0.ipmiPass)
    ipmiUser=root
    jumpserver_ip=$(ifconfig | grep -A 5 docker0 | grep "inet addr" | cut -d ':' -f 2 | cut -d ' ' -f 1)

    cat << EOF >${DOVETAIL_CONFIG}/pod.yaml
nodes:
- {ip: ${jumpserver_ip}, name: node0, password: root, role: Jumpserver, user: root}
- {ip: 10.1.0.50, name: node1, password: root, role: controller, user: root,
   ipmi_ip: ${ipmiIp}, ipmi_user: ${ipmiUser}, ipmi_password: ${ipmiPass}}
- {ip: 10.1.0.51, name: node2, password: root, role: controller, user: root}
- {ip: 10.1.0.52, name: node3, password: root, role: controller, user: root}
- {ip: 10.1.0.53, name: node4, password: root, role: compute, user: root}
- {ip: 10.1.0.54, name: node5, password: root, role: compute, user: root}

EOF
fi

if [[ ! "${SUT_BRANCH}" =~ "danube" && ${INSTALLER_TYPE} == 'fuel' && ${DEPLOY_TYPE} == 'baremetal' ]]; then
    fuel_ctl_ssh_options="${ssh_options} -i ${SSH_KEY}"
    ssh_user="ubuntu"
    fuel_ctl_ip=$(ssh 2>/dev/null ${fuel_ctl_ssh_options} "${ssh_user}@${INSTALLER_IP}" \
            "sudo salt --out yaml 'ctl*' pillar.get _param:openstack_control_address | \
                awk '{print \$2; exit}'") &> /dev/null
    cat << EOF >${DOVETAIL_CONFIG}/pod.yaml
nodes:
- {ip: ${fuel_ctl_ip}, name: node1, key_filename: /root/.ssh/id_rsa, role: controller, user: ${ssh_user}}

EOF
fi

if [[ ! -f ${DOVETAIL_CONFIG}/pod.yaml ]]; then
    set +e

    sudo pip install virtualenv

    cd ${releng_repo}/modules
    sudo virtualenv venv
    source venv/bin/activate
    sudo pip install -e ./ >/dev/null
    sudo pip install netaddr

    if [[ ${INSTALLER_TYPE} == compass ]]; then
        options="-u root -p root"
    elif [[ ${INSTALLER_TYPE} == fuel ]]; then
        options="-u root -p r00tme"
    elif [[ ${INSTALLER_TYPE} == apex ]]; then
        options="-u stack -k /root/.ssh/id_rsa"
    elif [[ ${INSTALLER_TYPE} == daisy ]]; then
        options="-u root -p r00tme"
    else
        echo "Don't support to generate pod.yaml on ${INSTALLER_TYPE} currently."
        echo "HA test cases may not run properly."
    fi

    cmd="sudo python ${releng_repo}/utils/create_pod_file.py -t ${INSTALLER_TYPE} \
         -i ${INSTALLER_IP} ${options} -f ${DOVETAIL_CONFIG}/pod.yaml"
    echo ${cmd}
    ${cmd}

    deactivate

    set -e

    cd ${WORKSPACE}
fi

if [ -f ${DOVETAIL_CONFIG}/pod.yaml ]; then
    sudo chmod 666 ${DOVETAIL_CONFIG}/pod.yaml
    echo "Adapt process info for $INSTALLER_TYPE ..."
    attack_process='rabbitmq'
    cat << EOF >> ${DOVETAIL_CONFIG}/pod.yaml
process_info:
- {testcase_name: dovetail.ha.tc010, attack_process: ${attack_process}}

EOF
    echo "file ${DOVETAIL_CONFIG}/pod.yaml:"
    cat ${DOVETAIL_CONFIG}/pod.yaml
else
    echo "Error: cannot find file ${DOVETAIL_CONFIG}/pod.yaml. Please check if it is existing."
    sudo ls -al ${DOVETAIL_CONFIG}
    echo "HA test cases may not run properly."
fi

if [ "$INSTALLER_TYPE" == "fuel" ]; then
    if [[ "${SUT_BRANCH}" =~ "danube" ]]; then
        echo "Fetching id_rsa file from jump_server $INSTALLER_IP..."
        sshpass -p r00tme sudo scp $ssh_options root@${INSTALLER_IP}:~/.ssh/id_rsa ${DOVETAIL_CONFIG}/id_rsa
    else
        cp ${SSH_KEY} ${DOVETAIL_CONFIG}/id_rsa
    fi
fi

if [ "$INSTALLER_TYPE" == "apex" ]; then
    echo "Fetching id_rsa file from jump_server $INSTALLER_IP..."
    sudo scp $ssh_options stack@${INSTALLER_IP}:~/.ssh/id_rsa ${DOVETAIL_CONFIG}/id_rsa
fi

if [ "$INSTALLER_TYPE" == "daisy" ]; then
    echo "Fetching id_dsa file from jump_server $INSTALLER_IP..."
    sshpass -p r00tme sudo scp $ssh_options root@${INSTALLER_IP}:~/.ssh/id_dsa ${DOVETAIL_CONFIG}/id_rsa
fi


image_path=${HOME}/opnfv/dovetail/images
if [[ ! -d ${image_path} ]]; then
    mkdir -p ${image_path}
fi
# sdnvpn test case needs to download this image first before running
ubuntu_image=${image_path}/ubuntu-16.04-server-cloudimg-amd64-disk1.img
if [[ ! -f ${ubuntu_image} ]]; then
    echo "Download image ubuntu-16.04-server-cloudimg-amd64-disk1.img ..."
    wget -q -nc http://artifacts.opnfv.org/sdnvpn/ubuntu-16.04-server-cloudimg-amd64-disk1.img -P ${image_path}
fi
sudo cp ${ubuntu_image} ${DOVETAIL_IMAGES}

# yardstick and bottlenecks need to download this image first before running
cirros_image=${image_path}/cirros-0.3.5-x86_64-disk.img
if [[ ! -f ${cirros_image} ]]; then
    echo "Download image cirros-0.3.5-x86_64-disk.img ..."
    wget -q -nc http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img -P ${image_path}
fi
sudo cp ${cirros_image} ${DOVETAIL_IMAGES}

# functest needs to download this image first before running
cirros_image=${image_path}/cirros-0.4.0-x86_64-disk.img
if [[ ! -f ${cirros_image} ]]; then
    echo "Download image cirros-0.4.0-x86_64-disk.img ..."
    wget -q -nc http://download.cirros-cloud.net/0.4.0/cirros-0.4.0-x86_64-disk.img -P ${image_path}
fi
sudo cp ${cirros_image} ${DOVETAIL_IMAGES}

# snaps_smoke test case needs to download this image first before running
ubuntu14_image=${image_path}/ubuntu-14.04-server-cloudimg-amd64-disk1.img
if [[ ! -f ${ubuntu14_image} ]]; then
    echo "Download image ubuntu-14.04-server-cloudimg-amd64-disk1.img ..."
    wget -q -nc https://cloud-images.ubuntu.com/releases/14.04/release/ubuntu-14.04-server-cloudimg-amd64-disk1.img -P ${image_path}
fi
sudo cp ${ubuntu14_image} ${DOVETAIL_IMAGES}

# cloudify_ims test case needs to download these 2 images first before running
cloudify_image=${image_path}/cloudify-manager-premium-4.0.1.qcow2
if [[ ! -f ${cloudify_image} ]]; then
    echo "Download image cloudify-manager-premium-4.0.1.qcow2 ..."
    wget -q -nc http://repository.cloudifysource.org/cloudify/4.0.1/sp-release/cloudify-manager-premium-4.0.1.qcow2 -P ${image_path}
fi
sudo cp ${cloudify_image} ${DOVETAIL_IMAGES}
trusty_image=${image_path}/trusty-server-cloudimg-amd64-disk1.img
if [[ ! -f ${trusty_image} ]]; then
    echo "Download image trusty-server-cloudimg-amd64-disk1.img ..."
    wget -q -nc http://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img -P ${image_path}
fi
sudo cp ${trusty_image} ${DOVETAIL_IMAGES}

opts="--privileged=true -id"

docker_volume="-v /var/run/docker.sock:/var/run/docker.sock"
dovetail_home_volume="-v ${DOVETAIL_HOME}:${DOVETAIL_HOME}"

# Pull the image with correct tag
DOCKER_REPO='opnfv/dovetail'
if [ "$(uname -m)" = 'aarch64' ]; then
    DOCKER_REPO="${DOCKER_REPO}_$(uname -m)"
    DOCKER_TAG="latest"
fi

echo "Dovetail: Pulling image ${DOCKER_REPO}:${DOCKER_TAG}"
docker pull ${DOCKER_REPO}:$DOCKER_TAG >$redirect

cmd="docker run ${opts} -e DOVETAIL_HOME=${DOVETAIL_HOME} ${docker_volume} ${dovetail_home_volume} \
     ${sshkey} ${DOCKER_REPO}:${DOCKER_TAG} /bin/bash"
echo "Dovetail: running docker run command: ${cmd}"
${cmd} >${redirect}
sleep 5
container_id=$(docker ps | grep "${DOCKER_REPO}:${DOCKER_TAG}" | awk '{print $1}' | head -1)
echo "Container ID=${container_id}"
if [ -z ${container_id} ]; then
    echo "Cannot find ${DOCKER_REPO} container ID ${container_id}. Please check if it is existing."
    docker ps -a
    exit 1
fi
echo "Container Start: docker start ${container_id}"
docker start ${container_id}
sleep 5
docker ps >${redirect}
if [ $(docker ps | grep "${DOCKER_REPO}:${DOCKER_TAG}" | wc -l) == 0 ]; then
    echo "The container ${DOCKER_REPO} with ID=${container_id} has not been properly started. Exiting..."
    exit 1
fi

# Modify tempest_conf.yaml file
tempest_conf_file=${DOVETAIL_CONFIG}/tempest_conf.yaml
if [[ ${INSTALLER_TYPE} == 'compass' || ${INSTALLER_TYPE} == 'apex' ]]; then
    volume_device='vdb'
else
    volume_device='vdc'
fi

cat << EOF >$tempest_conf_file

compute:
    min_compute_nodes: 2
    volume_device_name: ${volume_device}

EOF

echo "${tempest_conf_file}..."
cat ${tempest_conf_file}

cp_tempest_cmd="docker cp ${DOVETAIL_CONFIG}/tempest_conf.yaml $container_id:/home/opnfv/dovetail/dovetail/userconfig"
echo "exec command: ${cp_tempest_cmd}"
$cp_tempest_cmd

if [[ ${TESTSUITE} == 'default' ]]; then
    testsuite=''
else
    testsuite="--testsuite ${TESTSUITE}"
fi

run_cmd="dovetail run ${testsuite} -d"
echo "Container exec command: ${run_cmd}"
docker exec $container_id ${run_cmd}

sudo cp -r ${DOVETAIL_HOME}/results ./
# To make sure the file owner is the current user, for the copied results files in the above line
echo "Change owner of result files ..."
CURRENT_USER=${SUDO_USER:-$USER}
PRIMARY_GROUP=$(id -gn $CURRENT_USER)
echo "Current user is ${CURRENT_USER}, group is ${PRIMARY_GROUP}"
sudo chown -R ${CURRENT_USER}:${PRIMARY_GROUP} ./results

#remove useless files to save disk space
sudo rm -rf ./results/workspace
sudo rm -f ./results/yardstick.img
sudo rm -f ./results/tmp*

echo "Dovetail: done!"

