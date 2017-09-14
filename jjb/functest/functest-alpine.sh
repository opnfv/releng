#!/bin/bash

set -e
set +u
set +o pipefail

[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"
FUNCTEST_DIR=/home/opnfv/functest
DEPLOY_TYPE=baremetal
[[ $BUILD_TAG =~ "virtual" ]] && DEPLOY_TYPE=virt
HOST_ARCH=$(uname -m)

# Prepare OpenStack credentials volume
rc_file=${HOME}/opnfv-openrc.sh

if [[ ${INSTALLER_TYPE} == 'joid' ]]; then
    rc_file=$LAB_CONFIG/admin-openrc
elif [[ ${INSTALLER_TYPE} == 'compass' && ${BRANCH} == 'master' ]]; then
    cacert_file_vol="-v ${HOME}/os_cacert:${FUNCTEST_DIR}/conf/os_cacert"
    echo "export OS_CACERT=${FUNCTEST_DIR}/conf/os_cacert" >> ${HOME}/opnfv-openrc.sh
elif [[ ${INSTALLER_TYPE} == 'fuel' && ${DEPLOY_TYPE} == 'baremetal' ]]; then
    cacert_file_vol="-v ${HOME}/os_cacert:/etc/ssl/certs/mcp_os_cacert"
fi
rc_file_vol="-v ${rc_file}:${FUNCTEST_DIR}/conf/openstack.creds"


# Set iptables rule to allow forwarding return traffic for container
if ! sudo iptables -C FORWARD -j RETURN 2> ${redirect} || ! sudo iptables -L FORWARD | awk 'NR==3' | grep RETURN 2> ${redirect}; then
    sudo iptables -I FORWARD -j RETURN
fi

echo "Functest: Start Docker and prepare environment"

echo "Functest: Download images that will be used by test cases"
images_dir="${HOME}/opnfv/functest/images"
download_script=${WORKSPACE}/functest/ci/download_images.sh
if [[ ! -f ${download_script} ]]; then
    # to support Danube as well
    wget https://git.opnfv.org/functest/plain/functest/ci/download_images.sh -O ${download_script} 2> ${redirect}
fi
chmod +x ${download_script}
${download_script} ${images_dir} ${DEPLOY_SCENARIO} ${HOST_ARCH} 2> ${redirect}

images_vol="-v ${images_dir}:${FUNCTEST_DIR}/images"

dir_result="${HOME}/opnfv/functest/results/${BRANCH##*/}"
mkdir -p ${dir_result}
sudo rm -rf ${dir_result}/*
results_vol="-v ${dir_result}:${FUNCTEST_DIR}/results"
custom_params=
test -f ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG} && custom_params=$(cat ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG})

envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP} \
    -e NODE_NAME=${NODE_NAME} -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
    -e BUILD_TAG=${BUILD_TAG} -e DEPLOY_TYPE=${DEPLOY_TYPE}"

ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

if [[ ${INSTALLER_TYPE} == 'compass' && ${DEPLOY_SCENARIO} == *'os-nosdn-openo-ha'* ]]; then
    openo_msb_port=${openo_msb_port:-80}
    openo_msb_endpoint="$(sshpass -p'root' ssh 2>/dev/null $ssh_options root@${installer_ip} \
    'mysql -ucompass -pcompass -Dcompass -e "select package_config from cluster;" \
    | sed s/,/\\n/g | grep openo_ip | cut -d \" -f 4'):$openo_msb_port"

    envs=${env}" -e OPENO_MSB_ENDPOINT=${openo_msb_endpoint}"
fi

if [ "${INSTALLER_TYPE}" == 'fuel' ] && [ "$BRANCH" != 'stable/danube' ]; then
    COMPUTE_ARCH=$(ssh -l ubuntu ${INSTALLER_IP} -i ${SSH_KEY} ${ssh_options} \
        "sudo salt 'cmp*' grains.get cpuarch --out yaml | awk '{print \$2; exit}'")
    envs="${envs} -e POD_ARCH=${COMPUTE_ARCH}"
fi

volumes="${images_vol} ${results_vol} ${sshkey_vol} ${rc_file_vol} ${cacert_file_vol}"

set +e

if [ ${FUNCTEST_SUITE_NAME} == 'healthcheck' ]; then
    tiers=(healthcheck)
else
    tiers=(healthcheck smoke features vnf)
fi

cmd_opt='prepare_env start && run_tests -r -t all'

for tier in ${tiers[@]}; do
    FUNCTEST_IMAGE=opnfv/functest-${tier}
    echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
    docker pull ${FUNCTEST_IMAGE}>/dev/null
    cmd="docker run ${envs} ${volumes} ${FUNCTEST_IMAGE} /bin/bash -c '${cmd_opt}'"
    echo "Running Functest tier '${tier}'. CMD: ${cmd}"
    eval ${cmd}
done
