#!/bin/bash

set -e
set +u
set +o pipefail

[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"
FUNCTEST_DIR=/home/opnfv/functest

rc_file=${HOME}/k8.creds
sudo rm -rf $rc_file

if [[ ${INSTALLER_TYPE} == 'compass' ]]; then
    admin_conf_file_vol="-v ${HOME}/admin.conf:/root/.kube/config"
    echo "export KUBERNETES_PROVIDER=local" >> $rc_file
    KUBE_MASTER_URL=$(cat ${HOME}/admin.conf|grep server| awk '{print $2}')
    echo "export KUBE_MASTER_URL=$KUBE_MASTER_URL" >> $rc_file
    KUBE_MASTER_IP=$(echo $KUBE_MASTER_URL|awk -F'https://|:[0-9]+' '$0=$2')
    echo "export KUBE_MASTER_IP=$KUBE_MASTER_IP" >> $rc_file
elif [[ ${INSTALLER_TYPE} == 'joid' && ${BRANCH} == 'master' ]]; then
    admin_conf_file_vol="-v ${HOME}/joid_config/config:/root/.kube/config"
    rc_file=${HOME}/joid_config/k8config
else
    echo "Not supported by other installers yet"
    exit 1
fi

rc_file_vol="-v ${rc_file}:${FUNCTEST_DIR}/conf/env_file"

dir_result="${HOME}/opnfv/functest/results/${BRANCH##*/}"
mkdir -p ${dir_result}
sudo rm -rf ${dir_result}/*
results_vol="-v ${dir_result}:${FUNCTEST_DIR}/results"

volumes="${rc_file_vol} ${results_vol} ${admin_conf_file_vol}"

envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} \
    -e NODE_NAME=${NODE_NAME} -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
    -e BUILD_TAG=${BUILD_TAG} -e DEPLOY_TYPE=${DEPLOY_TYPE}"

DOCKER_TAG=`[[ ${BRANCH##*/} == "master" ]] && echo "latest" || echo ${BRANCH##*/}`

set +e

ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
echo 0 > ${ret_val_file}

FUNCTEST_IMAGES="\
opnfv/functest-kubernetes-healthcheck:${DOCKER_TAG} \
opnfv/functest-kubernetes-smoke:${DOCKER_TAG} \
opnfv/functest-kubernetes-features:${DOCKER_TAG}"
cmd_opt="run_tests -r -t all"

for image in ${FUNCTEST_IMAGES}; do
    echo "Pulling Docker image ${image} ..."
    docker pull "${image}" >/dev/null
    cmd="docker run --rm ${envs} ${volumes} ${image} /bin/bash -c '${cmd_opt}'"
    echo "Running Functest k8s test cases, CMD: ${cmd}"
    eval ${cmd}
    ret_value=$?
    if [ ${ret_value} != 0 ]; then
        echo ${ret_value} > ${ret_val_file}
    fi
done
