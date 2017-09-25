#!/bin/bash

set -e
set +u
set +o pipefail

run_tiers() {
    cmd_opt='prepare_env start && run_tests -r -t all'
    ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
    echo 0 > ${ret_val_file}

    for tier in ${tiers[@]}; do
        FUNCTEST_IMAGE=opnfv/functest-${tier}
        echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
        docker pull ${FUNCTEST_IMAGE}>/dev/null
        cmd="docker run --privileged=true ${envs} ${volumes} ${FUNCTEST_IMAGE} /bin/bash -c '${cmd_opt}'"
        echo "Running Functest tier '${tier}'. CMD: ${cmd}"
        eval ${cmd}
        ret_value=$?
        if [ ${ret_value} != 0 ]; then
          echo ${ret_value} > ${ret_val_file}
        fi
    done
}

run_test() {
    test_name=$1
    cmd_opt='prepare_env start && run_tests -r -t $test_name'
    ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
    echo 0 > ${ret_val_file}
    # Determine which Functest image should be used for the test case
    case ${test_name} in
        connection_check|api_check|snaps_health_check)
            FUNCTEST_IMAGE=opnfv/functest-healthcheck
        vping_ssh|vping_userdata|tempest_smoke_serial|rally_sanity|refstack_defcore|odl|odl_netvirt|fds|snaps_smoke)
            FUNCTEST_IMAGE=opnfv/functest-smoke
        tempest_full_parallel|tempest_custom|rally_full)
            FUNCTEST_IMAGE=opnfv/functest-components
        cloudify_ims|orchestra_openims|orchestra_clearwaterims|vyos_vrouter)
            FUNCTEST_IMAGE=opnfv/functest-vnf
        promise|doctor-notification|bgpvpn|functest-odl-sfc|domino-multinode|barometercollectd)
            FUNCTEST_IMAGE=opnfv/functest-features
        parser)
            FUNCTEST_IMAGE=opnfv/functest-parser
        *)
            echo "Unkown test case $test_name"
            exit 1
    esac
    echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
    docker pull ${FUNCTEST_IMAGE}>/dev/null
    cmd="docker run --privileged=true ${envs} ${volumes} ${FUNCTEST_IMAGE} /bin/bash -c '${cmd_opt}'"
    echo "Running Functest test case '${test_name}'. CMD: ${cmd}"
    eval ${cmd}
    ret_value=$?
    if [ ${ret_value} != 0 ]; then
      echo ${ret_value} > ${ret_val_file}
    fi
}


[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"
FUNCTEST_DIR=/home/opnfv/functest
DEPLOY_TYPE=baremetal
[[ $BUILD_TAG =~ "virtual" ]] && DEPLOY_TYPE=virt
HOST_ARCH=$(uname -m)

# Prepare OpenStack credentials volume
rc_file=${HOME}/opnfv-openrc.sh

if [[ ${INSTALLER_TYPE} == 'joid' ]]; then
    rc_file=$LAB_CONFIG/admin-openrc
elif [[ ${INSTALLER_TYPE} == 'compass' ]]; then
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


if [ "${INSTALLER_TYPE}" == 'fuel' ]; then
    COMPUTE_ARCH=$(ssh -l ubuntu ${INSTALLER_IP} -i ${SSH_KEY} ${ssh_options} \
        "sudo salt 'cmp*' grains.get cpuarch --out yaml | awk '{print \$2; exit}'")
    envs="${envs} -e POD_ARCH=${COMPUTE_ARCH}"
fi

volumes="${images_vol} ${results_vol} ${sshkey_vol} ${rc_file_vol} ${cacert_file_vol}"

set +e


if [[ ${DEPLOY_SCENARIO} =~ ^os-.* ]]; then
    if [ ${FUNCTEST_MODE} == 'testcase' ]; then
        run_test ${FUNCTEST_SUITE_NAME}
    elif [ ${FUNCTEST_MODE} == 'tier' ]; then
        tiers= (${FUNCTEST_TIER})
        run_tiers ${tiers}
    else
        if [ ${DEPLOY_TYPE} == 'baremetal' ]; then
            tiers=(healthcheck smoke features vnf parser)
        else
            tiers=(healthcheck smoke features)
        fi
        run_tiers ${tiers}
    fi
else
    echo "k8 deployment has not been supported by functest yet"
fi
