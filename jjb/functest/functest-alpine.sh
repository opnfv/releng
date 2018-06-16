#!/bin/bash

set -e
set +u
set +o pipefail

REPO=${REPO:-opnfv}
CI_LOOP=${CI_LOOP:-daily}
TEST_DB_URL=http://testresults.opnfv.org/test/api/v1/results
ENERGY_RECORDER_API_URL=http://energy.opnfv.fr/resources

check_os_deployment() {
    FUNCTEST_IMAGE=${REPO}/functest-healthcheck:${DOCKER_TAG}
    echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
    docker pull ${FUNCTEST_IMAGE}>/dev/null
    cmd="docker run --rm ${volumes} ${FUNCTEST_IMAGE} check_deployment"
    echo "Checking deployment, CMD: ${cmd}"
    eval ${cmd}
    ret_value=$?
    if [ ${ret_value} != 0 ]; then
        echo "ERROR: Problem while checking OpenStack deployment."
        exit 1
    else
        echo "OpenStack deployment OK."
    fi

}


run_tiers() {
    tiers=$1
    cmd_opt="run_tests -r -t all"
    [[ $BUILD_TAG =~ "suite" ]] && cmd_opt="run_tests -t all"
    ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
    echo 0 > ${ret_val_file}

    for tier in ${tiers[@]}; do
        FUNCTEST_IMAGE=${REPO}/functest-${tier}:${DOCKER_TAG}
        echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
        docker pull ${FUNCTEST_IMAGE}>/dev/null
        cmd="docker run --rm  ${envs} ${volumes} ${TESTCASE_OPTIONS} ${FUNCTEST_IMAGE} /bin/bash -c '${cmd_opt}'"
        echo "Running Functest tier '${tier}'. CMD: ${cmd}"
        eval ${cmd}
        ret_value=$?
        if [ ${ret_value} != 0 ]; then
            echo ${ret_value} > ${ret_val_file}
            if [ ${tier} == 'healthcheck' ]; then
                echo "Healthcheck tier failed. Exiting Functest..."
                break
            fi
        fi
    done
}

run_test() {
    test_name=$1
    cmd_opt="run_tests -t ${test_name}"
    ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
    echo 0 > ${ret_val_file}
    # Determine which Functest image should be used for the test case
    case ${test_name} in
        connection_check|api_check|snaps_health_check)
            FUNCTEST_IMAGE=${REPO}/functest-healthcheck:${DOCKER_TAG} ;;
        vping_ssh|vping_userdata|cinder_test|tempest_smoke_serial|rally_sanity|refstack_defcore|patrole|odl|snaps_smoke|neutron_trunk)
            FUNCTEST_IMAGE=${REPO}/functest-smoke:${DOCKER_TAG} ;;
        tempest_full_parallel|rally_full)
            FUNCTEST_IMAGE=${REPO}/functest-components:${DOCKER_TAG} ;;
        cloudify_ims|vyos_vrouter|juju_epc)
            FUNCTEST_IMAGE=${REPO}/functest-vnf:${DOCKER_TAG} ;;
        doctor-notification|bgpvpn|functest-odl-sfc|domino-multinode|barometercollectd|fds)
            FUNCTEST_IMAGE=${REPO}/functest-features:${DOCKER_TAG} ;;
        parser-basics)
            FUNCTEST_IMAGE=${REPO}/functest-parser:${DOCKER_TAG} ;;
        *)
            echo "Unkown test case $test_name"
            exit 1
            ;;
    esac
    echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
    docker pull ${FUNCTEST_IMAGE}>/dev/null
    cmd="docker run --rm ${envs} ${volumes} ${TESTCASE_OPTIONS} ${FUNCTEST_IMAGE} /bin/bash -c '${cmd_opt}'"
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
DOCKER_TAG=`[[ ${BRANCH##*/} == "master" ]] && echo "latest" || echo ${BRANCH##*/}`

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

rc_file_vol="-v ${rc_file}:${FUNCTEST_DIR}/conf/env_file"

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
    -e BUILD_TAG=${BUILD_TAG} -e DEPLOY_TYPE=${DEPLOY_TYPE} -e CI_LOOP=${CI_LOOP} \
    -e TEST_DB_URL=${TEST_DB_URL} -e ENERGY_RECORDER_API_URL=${ENERGY_RECORDER_API_URL}"

ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"


if [ "${INSTALLER_TYPE}" == 'fuel' ]; then
    COMPUTE_ARCH=$(ssh -l ubuntu ${INSTALLER_IP} -i ${SSH_KEY} ${ssh_options} \
        "sudo salt 'cmp*' grains.get cpuarch --out yaml | awk '{print \$2; exit}'")
    envs="${envs} -e POD_ARCH=${COMPUTE_ARCH}"
fi


if [[ ${INSTALLER_TYPE} == 'compass' && ${DEPLOY_SCENARIO} =~ 'sfc' ]]; then
    ssh_key="/tmp/id_rsa"
    user_config="/tmp/openstack_user_config.yml"
    docker cp compass-tasks:/root/.ssh/id_rsa $ssh_key
    docker cp compass-tasks:/etc/openstack_deploy/openstack_user_config.yml $user_config
    sshkey_vol="-v ${ssh_key}:/root/.ssh/id_rsa"
    userconfig_vol="-v ${user_config}:${user_config}"
    envs="${envs} -e EXTERNAL_NETWORK=${EXTERNAL_NETWORK}"
fi


volumes="${images_vol} ${results_vol} ${sshkey_vol} ${userconfig_vol} ${rc_file_vol} ${cacert_file_vol}"

set +e

if [ ${FUNCTEST_MODE} == 'testcase' ]; then
    echo "FUNCTEST_MODE=testcase, FUNCTEST_SUITE_NAME=${FUNCTEST_SUITE_NAME}"
    run_test ${FUNCTEST_SUITE_NAME}
elif [ ${FUNCTEST_MODE} == 'tier' ]; then
    echo "FUNCTEST_MODE=tier, FUNCTEST_TIER=${FUNCTEST_TIER}"
    tiers=(${FUNCTEST_TIER})
    run_tiers ${tiers}
else
    if [ ${DEPLOY_TYPE} == 'baremetal' ] && [ "${HOST_ARCH}" != "aarch64" ]; then
        if [[ ${BRANCH} == "stable/fraser" ]]; then
            tiers=(healthcheck smoke features vnf parser)
        else
            tiers=(healthcheck smoke features vnf)
        fi
    else
        if [[ ${BRANCH} == "stable/fraser" ]]; then
            tiers=(healthcheck smoke features parser)
        else
            tiers=(healthcheck smoke features)
        fi
    fi
    run_tiers ${tiers}
fi
