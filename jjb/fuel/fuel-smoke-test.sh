#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2017 Ericsson AB, Mirantis Inc., Enea Software AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -e
set +u
set +o pipefail

CI_LOOP=${CI_LOOP:-daily}
TEST_DB_URL=http://testresults.opnfv.org/test/api/v1/results
ENERGY_RECORDER_API_URL=http://energy.opnfv.fr/resources

check_os_deployment() {
    FUNCTEST_IMAGE=opnfv/functest-healthcheck:${DOCKER_TAG}
    echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
    docker pull ${FUNCTEST_IMAGE}>/dev/null
    cmd="docker run --rm --privileged=true ${volumes} ${FUNCTEST_IMAGE} check_deployment"
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
    if [[ ${BRANCH##*/} == "master" ]]; then
        cmd_opt="run_tests -r -t all"
        [[ $BUILD_TAG =~ "suite" ]] && cmd_opt="run_tests -t all"
    else
        cmd_opt="prepare_env start && run_tests -r -t all"
        [[ $BUILD_TAG =~ "suite" ]] && cmd_opt="prepare_env start && run_tests -t all"
    fi
    ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
    echo 0 > ${ret_val_file}

    for tier in ${tiers[@]}; do
        FUNCTEST_IMAGE=opnfv/functest-${tier}:${DOCKER_TAG}
        echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
        docker pull ${FUNCTEST_IMAGE}>/dev/null
        cmd="docker run --rm  --privileged=true ${envs} ${volumes} ${TESTCASE_OPTIONS} ${FUNCTEST_IMAGE} /bin/bash -c '${cmd_opt}'"
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


[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"
FUNCTEST_DIR=/home/opnfv/functest
DEPLOY_TYPE=baremetal
[[ $BUILD_TAG =~ "virtual" ]] && DEPLOY_TYPE=virt
HOST_ARCH=$(uname -m)
DOCKER_TAG=`[[ ${BRANCH##*/} == "master" ]] && echo "latest" || echo ${BRANCH##*/}`

# Prepare OpenStack credentials volume
rc_file=${HOME}/opnfv-openrc.sh

if [[ ${INSTALLER_TYPE} == 'fuel' && ${DEPLOY_TYPE} == 'baremetal' ]]; then
    cacert_file_vol="-v ${HOME}/os_cacert:/etc/ssl/certs/mcp_os_cacert"
fi

if [[ ${BRANCH} == "stable/euphrates" ]]; then
    rc_file_vol="-v ${rc_file}:${FUNCTEST_DIR}/conf/openstack.creds"
else
    rc_file_vol="-v ${rc_file}:${FUNCTEST_DIR}/conf/env_file"
fi

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
    -e BUILD_TAG=${BUILD_TAG} -e DEPLOY_TYPE=${DEPLOY_TYPE} -e CI_LOOP=${CI_LOOP} \
    -e TEST_DB_URL=${TEST_DB_URL} -e ENERGY_RECORDER_API_URL=${ENERGY_RECORDER_API_URL}"

ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"


if [ "${INSTALLER_TYPE}" == 'fuel' ]; then
    COMPUTE_ARCH=$(ssh -l ubuntu ${INSTALLER_IP} -i ${SSH_KEY} ${ssh_options} \
        "sudo salt 'cmp*' grains.get cpuarch --out yaml | awk '{print \$2; exit}'")
    envs="${envs} -e POD_ARCH=${COMPUTE_ARCH}"
fi

volumes="${images_vol} ${results_vol} ${rc_file_vol} ${cacert_file_vol}"

set +e

[[ ${BRANCH##*/} == "master" ]] && check_os_deployment

# run testsuite healthcheck
tiers=('healthcheck')
run_tiers ${tiers}
