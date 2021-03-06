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

DOVETAIL_HOME=${WORKSPACE}/ovp
[ -d ${DOVETAIL_HOME} ] && sudo rm -rf ${DOVETAIL_HOME}

mkdir -p ${DOVETAIL_HOME}

DOVETAIL_CONFIG=${DOVETAIL_HOME}/pre_config
mkdir -p ${DOVETAIL_CONFIG}

DOVETAIL_IMAGES=${DOVETAIL_HOME}/images
mkdir -p ${DOVETAIL_IMAGES}

OPENRC=${DOVETAIL_CONFIG}/env_config.sh
CACERT=${DOVETAIL_CONFIG}/os_cacert
POD=${DOVETAIL_CONFIG}/pod.yaml

ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

sshkey=""

TEST_DB_URL=http://testresults.opnfv.org/test/api/v1/results

check_file_exists() {
    if [[ -f $1 ]]; then
        echo 0
    else
        echo 1
    fi
}

get_cred_file_with_scripts() {
    echo "INFO: clone releng repo..."
    releng_repo=${WORKSPACE}/releng
    [ -d ${releng_repo} ] && sudo rm -rf ${releng_repo}
    git clone https://gerrit.opnfv.org/gerrit/releng ${releng_repo} >/dev/null

    echo "INFO: clone pharos repo..."
    pharos_repo=${WORKSPACE}/pharos
    [ -d ${pharos_repo} ] && sudo rm -rf ${pharos_repo}
    git clone https://git.opnfv.org/pharos ${pharos_repo} >/dev/null

    echo "INFO: SUT branch is $SUT_BRANCH"
    echo "INFO: dovetail branch is $BRANCH"
    BRANCH_BACKUP=$BRANCH
    export BRANCH=$SUT_BRANCH
    cmd="${releng_repo}/utils/fetch_os_creds.sh -d ${OPENRC} -i ${INSTALLER_TYPE} -a ${INSTALLER_IP} -o ${CACERT} >${redirect}"
    echo "INFO: cmd is ${cmd}"
    ${cmd}
    export BRANCH=$BRANCH_BACKUP
}

get_apex_cred_file() {
    instack_mac=$(sudo virsh domiflist undercloud | grep default | \
                  grep -Eo "[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+:[0-9a-f]+")
    INSTALLER_IP=$(/usr/sbin/arp -e | grep ${instack_mac} | awk {'print $1'})
    sshkey="-v /root/.ssh/id_rsa:/root/.ssh/id_rsa"
    if [[ -n $(sudo iptables -L FORWARD |grep "REJECT"|grep "reject-with icmp-port-unreachable") ]]; then
        #note: this happens only in opnfv-lf-pod1
        sudo iptables -D FORWARD -o virbr0 -j REJECT --reject-with icmp-port-unreachable
        sudo iptables -D FORWARD -i virbr0 -j REJECT --reject-with icmp-port-unreachable
    fi
    get_cred_file_with_scripts
}

get_fuel_cred_file() {
    get_cred_file_with_scripts
}

get_joid_cred_file() {
    # If production lab then creds may be retrieved dynamically
    # creds are on the jumphost, always in the same folder
    sudo cp $LAB_CONFIG/admin-openrc $OPENRC
}

change_cred_file_cacert_path() {
    if [[ ${INSTALLER_TYPE} == "apex" ]]; then
        echo "INFO: apex doesn't need to set OS_CACERT."
        return 0
    fi
    exists=`check_file_exists ${CACERT}`
    if [[ $exists == 0 ]]; then
        echo "INFO: set ${INSTALLER_TYPE} openstack cacert file to be ${CACERT}"
        if [[ ${INSTALLER_TYPE} == "fuel" ]]; then
            sed -i "s#/etc/ssl/certs/mcp_os_cacert#${CACERT}#g" ${OPENRC}
        fi
    else
        echo "ERROR: cannot find file ${CACERT}. Please check if it exists."
        sudo ls -al ${DOVETAIL_CONFIG}
        exit 1
    fi
}

change_cred_file_ext_net() {
    exists=`check_file_exists ${OPENRC}`
    if [[ $exists == 0 ]]; then
        echo "export EXTERNAL_NETWORK=${EXTERNAL_NETWORK}" >> ${OPENRC}
    else
        echo "ERROR: cannot find file $OPENRC. Please check if it exists."
        sudo ls -al ${DOVETAIL_CONFIG}
        exit 1
    fi
}

get_cred_file() {
    if [[ ${INSTALLER_TYPE} == 'apex' ]]; then
        get_apex_cred_file
    elif [[ ${INSTALLER_TYPE} == 'fuel' ]]; then
        get_fuel_cred_file
    elif [[ ${INSTALLER_TYPE} == 'joid' ]]; then
        get_joid_cred_file
    fi

    exists=`check_file_exists ${OPENRC}`
    if [[ $exists == 0 ]]; then
        echo "INFO: original openstack credentials file is:"
        cat $OPENRC
        echo "INFO: change cacert file path in credentials file"
        change_cred_file_cacert_path
        #echo "INFO: set external network in credentials file"
        #change_cred_file_ext_net
        echo "INFO: final openstack credentials file is:"
        cat $OPENRC
    else
        echo "ERROR: cannot find file $OPENRC. Please check if it exists."
        sudo ls -al ${DOVETAIL_CONFIG}
        exit 1
    fi
}

get_fuel_baremetal_pod_file() {
    fuel_ctl_ssh_options="${ssh_options} -i ${SSH_KEY}"
    ssh_user="ubuntu"
    fuel_ctl_ip=$(ssh 2>/dev/null ${fuel_ctl_ssh_options} "${ssh_user}@${INSTALLER_IP}" \
            "sudo salt 'cfg*' pillar.get _param:openstack_control_address --out text| \
                cut -f2 -d' '")
    fuel_cmp_ip=$(ssh 2>/dev/null ${fuel_ctl_ssh_options} "${ssh_user}@${INSTALLER_IP}" \
            "sudo salt 'cmp001*' pillar.get _param:openstack_control_address --out text| \
                cut -f2 -d' '")
    fuel_dbs_ip=$(ssh 2>/dev/null ${fuel_ctl_ssh_options} "${ssh_user}@${INSTALLER_IP}" \
            "sudo salt 'dbs01*' pillar.get _param:openstack_database_node01_address --out text| \
                cut -f2 -d' '")
    fuel_msg_ip=$(ssh 2>/dev/null ${fuel_ctl_ssh_options} "${ssh_user}@${INSTALLER_IP}" \
            "sudo salt 'msg01*' pillar.get _param:openstack_message_queue_node01_address --out text| \
                cut -f2 -d' '")
    ipmi_index=$(ssh 2>/dev/null ${fuel_ctl_ssh_options} "${ssh_user}@${INSTALLER_IP}" \
            "sudo salt 'ctl*' network.ip_addrs cidr=${fuel_ctl_ip} --out text | grep ${fuel_ctl_ip} | cut -c 5")

    organization="$(cut -d'-' -f1 <<< "${NODE_NAME}")"
    pod_name="$(cut -d'-' -f2 <<< "${NODE_NAME}")"
    pdf_file=${pharos_repo}/labs/${organization}/${pod_name}.yaml
    ipmiIp=$(cat ${pdf_file} | shyaml get-value nodes.$[ipmi_index-1].remote_management.address)
    ipmiIp="$(cut -d'/' -f1 <<< "${ipmiIp}")"
    ipmiPass=$(cat ${pdf_file} | shyaml get-value nodes.$[ipmi_index-1].remote_management.pass)
    ipmiUser=$(cat ${pdf_file} | shyaml get-value nodes.$[ipmi_index-1].remote_management.user)
    [[ $ipmiUser == ENC* ]] && ipmiUser=$(eyaml decrypt -s ${ipmiUser//[[:blank:]]/})
    [[ $ipmiPass == ENC* ]] && ipmiPass=$(eyaml decrypt -s ${ipmiPass//[[:blank:]]/})

    cat << EOF >${POD}
nodes:
- {ip: ${INSTALLER_IP}, name: node0, key_filename: ${DOVETAIL_CONFIG}/id_rsa,
   role: Jumpserver, user: ${ssh_user}}
- {ip: ${fuel_ctl_ip}, name: node1, key_filename: ${DOVETAIL_CONFIG}/id_rsa,
   role: controller, user: ${ssh_user}, ipmi_ip: ${ipmiIp}, ipmi_user: ${ipmiUser}, ipmi_password: ${ipmiPass}}
- {ip: ${fuel_msg_ip}, name: msg01, key_filename: ${DOVETAIL_CONFIG}/id_rsa, role: controller, user: ${ssh_user}}
- {ip: ${fuel_cmp_ip}, name: cmp01, key_filename: ${DOVETAIL_CONFIG}/id_rsa, role: controller, user: ${ssh_user}}
- {ip: ${fuel_dbs_ip}, name: dbs01, key_filename: ${DOVETAIL_CONFIG}/id_rsa, role: controller, user: ${ssh_user}}
EOF
}

get_pod_file_with_scripts() {
    set +e
    sudo pip install virtualenv

    cd ${releng_repo}/modules
    sudo virtualenv venv
    source venv/bin/activate
    sudo pip install -e ./ >/dev/null
    sudo pip install netaddr

    if [[ ${INSTALLER_TYPE} == fuel ]]; then
        options="-u ubuntu -k /root/.ssh/id_rsa"
    elif [[ ${INSTALLER_TYPE} == apex ]]; then
        options="-u stack -k /root/.ssh/id_rsa"
    elif [[ ${INSTALLER_TYPE} == daisy ]]; then
        options="-u root -p r00tme"
    else
        echo "WARNING: Don't support to generate ${POD} on ${INSTALLER_TYPE} currently."
        echo "WARNING: HA test cases may not run properly."
    fi

    cmd="sudo python ${releng_repo}/utils/create_pod_file.py -t ${INSTALLER_TYPE} \
         -i ${INSTALLER_IP} ${options} -f ${POD} \
         -s ${DOVETAIL_CONFIG}/id_rsa"
    echo "INFO: cmd is ${cmd}"
    ${cmd}

    deactivate
    set -e
    cd ${WORKSPACE}
}

change_apex_pod_file_process_info() {
    cat << EOF >> ${POD}
process_info:
- {testcase_name: yardstick.ha.rabbitmq, attack_process: rabbitmq_server}
- {testcase_name: yardstick.ha.cinder_api, attack_process: cinder_wsgi}
EOF
}

change_fuel_pod_file_process_info() {
    cat << EOF >> ${POD}
process_info:
- {testcase_name: yardstick.ha.cinder_api, attack_process: cinder-wsgi}
- {testcase_name: yardstick.ha.rabbitmq, attack_process: rabbitmq_server, attack_host: msg01}
- {testcase_name: yardstick.ha.neutron_l3_agent, attack_process: neutron-l3-agent, attack_host: cmp01}
- {testcase_name: yardstick.ha.database, attack_process: mysqld, attack_host: dbs01}
EOF
}

change_pod_file_process_info() {
    sudo chmod 666 ${POD}
    echo "INFO: adapt process info for $INSTALLER_TYPE ..."
    if [ "$INSTALLER_TYPE" == "apex" ]; then
        change_apex_pod_file_process_info
    elif [ "$INSTALLER_TYPE" == "fuel" ]; then
        change_fuel_pod_file_process_info
    fi
}

get_pod_file() {
    # These packages are used for parsing yaml files and decrypting ipmi user and password.
    sudo pip install shyaml
    sudo yum install -y rubygems || sudo apt-get install -y ruby
    sudo gem install hiera-eyaml
    if [[ ${INSTALLER_TYPE} == 'fuel' && ${DEPLOY_TYPE} == 'baremetal' ]]; then
        get_fuel_baremetal_pod_file
    fi

    exists=`check_file_exists ${POD}`
    if [[ $exists == 1 ]]; then
        get_pod_file_with_scripts
    fi

    exists=`check_file_exists ${POD}`
    if [[ $exists == 0 ]]; then
        change_pod_file_process_info
    else
        echo "ERROR: cannot find file ${POD}. Please check if it exists."
        sudo ls -al ${DOVETAIL_CONFIG}
        exit 1
    fi

    echo "INFO: file ${POD} is:"
    cat ${POD}
}

get_cred_file
get_pod_file

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
    wget -q -nc https://artifacts.opnfv.org/sdnvpn/ubuntu-16.04-server-cloudimg-amd64-disk1.img -P ${image_path}
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

cmd="docker run ${opts} -e DOVETAIL_HOME=${DOVETAIL_HOME} -e INSTALLER_TYPE=${INSTALLER_TYPE} \
     -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} -e NODE_NAME=${NODE_NAME} -e BUILD_TAG=${BUILD_TAG} \
     -e TEST_DB_URL=${TEST_DB_URL} -e VERSION=${SUT_BRANCH} \
     ${docker_volume} ${dovetail_home_volume} \
     ${sshkey} ${DOCKER_REPO}:${DOCKER_TAG} /bin/bash"
echo "Dovetail: running docker run command: ${cmd}"
${cmd} >${redirect}
sleep 5
container_id=$(docker ps | grep "${DOCKER_REPO}:${DOCKER_TAG}" | awk '{print $1}' | head -1)
echo "Container ID=${container_id}"
if [ -z ${container_id} ]; then
    echo "Cannot find ${DOCKER_REPO} container ID ${container_id}. Please check if it exists."
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
if [[ ${INSTALLER_TYPE} == 'apex' ]]; then
    volume_device='vdb'
else
    volume_device='vdc'
fi

cat << EOF >$tempest_conf_file

compute:
    min_compute_nodes: 2
    volume_device_name: ${volume_device}
    max_microversion: 2.65

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

if [[ ${TESTAREA} == 'mandatory' ]]; then
    testarea='--mandatory'
elif [[ ${TESTAREA} == 'optional' ]]; then
    testarea="--optional"
elif [[ ${TESTAREA} == 'all' ]]; then
    testarea=""
else
    testarea="--testarea ${TESTAREA}"
fi

run_cmd="dovetail run ${testsuite} ${testarea} --deploy-scenario ${DEPLOY_SCENARIO} -d -r --opnfv-ci"
echo "Container exec command: ${run_cmd}"
docker exec $container_id ${run_cmd}

sudo cp -r ${DOVETAIL_HOME}/results ./
result_package=$(find ${DOVETAIL_HOME} -name 'logs_*')
echo "Results package is ${result_package}"
for item in ${result_package};
do
  sudo mv ${item} ./results
done

# To make sure the file owner is the current user, for the copied results files in the above line
echo "Change owner of result files ..."
CURRENT_USER=${SUDO_USER:-$USER}
PRIMARY_GROUP=$(id -gn $CURRENT_USER)
echo "Current user is ${CURRENT_USER}, group is ${PRIMARY_GROUP}"
sudo chown -R ${CURRENT_USER}:${PRIMARY_GROUP} ./results

#remove useless files to save disk space
sudo rm -rf ./results/workspace
sudo rm -f ./results/yardstick.img
sudo rm -f ./results/bottlenecks/tmp*

echo "Dovetail: done!"

