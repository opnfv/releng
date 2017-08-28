#!/bin/bash

set -e
set +u
set +o pipefail

[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

DEPLOY_TYPE=baremetal
[[ $BUILD_TAG =~ "virtual" ]] && DEPLOY_TYPE=virt
HOST_ARCH=$(uname -m)

# Prepare OpenStack credentials volume
rc_file_vol="-v ${HOME}/opnfv-openrc.sh:/home/opnfv/functest/conf/openstack.creds"

if [[ ${INSTALLER_TYPE} == 'joid' ]]; then
    rc_file_vol="-v $LAB_CONFIG/admin-openrc:/home/opnfv/functest/conf/openstack.creds"
elif [[ ${INSTALLER_TYPE} == 'compass' && ${BRANCH} == 'master' ]]; then
    cacert_file_vol="-v ${HOME}/os_cacert:/home/opnfv/functest/conf/os_cacert"
    echo "export OS_CACERT=/home/opnfv/functest/conf/os_cacert" >> ${HOME}/opnfv-openrc.sh
elif [[ ${INSTALLER_TYPE} == 'fuel' && ${DEPLOY_TYPE} == 'baremetal' ]]; then
    cacert_file_vol="-v ${HOME}/os_cacert:/etc/ssl/certs/mcp_os_cacert"
fi


# Set iptables rule to allow forwarding return traffic for container
if ! sudo iptables -C FORWARD -j RETURN 2> ${redirect} || ! sudo iptables -L FORWARD | awk 'NR==3' | grep RETURN 2> ${redirect}; then
    sudo iptables -I FORWARD -j RETURN
fi

echo "Functest: Start Docker and prepare environment"

if [ "$BRANCH" != 'stable/danube' ]; then
  echo "Functest: Download images that will be used by test cases"
  images_dir="${HOME}/opnfv/functest/images"
  chmod +x ${WORKSPACE}/functest/ci/download_images.sh
  ${WORKSPACE}/functest/ci/download_images.sh ${images_dir} > ${redirect} 2>&1
  images_vol="-v ${images_dir}:/home/opnfv/functest/images"
  echo "Functest: Images successfully downloaded"
fi

dir_result="${HOME}/opnfv/functest/results/${BRANCH##*/}"
mkdir -p ${dir_result}
sudo rm -rf ${dir_result}/*
results_vol="-v ${dir_result}:/home/opnfv/functest/results"
custom_params=
test -f ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG} && custom_params=$(cat ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG})
echo "Functest: custom parameters successfully retrieved: ${custom_params}"

envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP} \
    -e NODE_NAME=${NODE_NAME} -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
    -e BUILD_TAG=${BUILD_TAG} -e CI_DEBUG=${CI_DEBUG} -e DEPLOY_TYPE=${DEPLOY_TYPE}"

if [[ ${INSTALLER_TYPE} == 'fuel' && ! -z ${SALT_MASTER_IP} ]]; then
  HOST_ARCH=$(ssh -l ubuntu ${SALT_MASTER_IP} -i ${SSH_KEY} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no \
  "sudo salt 'cmp*' grains.get cpuarch --out yaml |awk '{print \$2; exit}'")
  envs="${envs} -e POD_ARCH=${HOST_ARCH}"
fi

if [[ ${INSTALLER_TYPE} == 'compass' && ${DEPLOY_SCENARIO} == *'os-nosdn-openo-ha'* ]]; then
    ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    openo_msb_port=${openo_msb_port:-80}
    openo_msb_endpoint="$(sshpass -p'root' ssh 2>/dev/null $ssh_options root@${installer_ip} \
    'mysql -ucompass -pcompass -Dcompass -e "select package_config from cluster;" \
    | sed s/,/\\n/g | grep openo_ip | cut -d \" -f 4'):$openo_msb_port"

    envs=${env}" -e OPENO_MSB_ENDPOINT=${openo_msb_endpoint}"
fi

if [ "$BRANCH" != 'stable/danube' ]; then
  volumes="${images_vol} ${results_vol} ${sshkey_vol} ${stackrc_vol} ${rc_file_vol} ${cacert_file_vol}"
else
  volumes="${results_vol} ${sshkey_vol} ${stackrc_vol} ${rc_file_vol}"
fi

echo "Functest: volumes defined"

FUNCTEST_IMAGE="opnfv/functest"
if [ "$HOST_ARCH" = "aarch64" ]; then
    FUNCTEST_IMAGE="${FUNCTEST_IMAGE}_${HOST_ARCH}"
fi

echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE}:${DOCKER_TAG}"
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

if [ "$BRANCH" == 'master' ]; then
    cmd="prepare_env start"
else
    cmd="python ${FUNCTEST_REPO_DIR}/functest/ci/prepare_env.py start"
fi


echo "Executing command inside the docker: ${cmd}"
docker exec ${container_id} ${cmd}
