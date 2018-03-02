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
    echo "export KUBECONFIG=/root/.kube/config" >> $rc_file
    echo "export KUBERNETES_PROVIDER=local" >> $rc_file
    KUBE_MASTER_URL=$(cat ${HOME}/admin.conf|grep server| awk '{print $2}')
    echo "export KUBE_MASTER_URL=$KUBE_MASTER_URL" >> $rc_file
    KUBE_MASTER_IP=$(echo $KUBE_MASTER_URL|awk -F'https://|:[0-9]+' '$0=$2')
    echo "export KUBE_MASTER_IP=$KUBE_MASTER_IP" >> $rc_file
elif [[ ${INSTALLER_TYPE} == 'joid' && ${BRANCH} == 'master' ]]; then
    admin_conf_file_vol="-v ${HOME}/joid_config/config:/root/joid_config/config"
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

# Set iptables rule to allow forwarding return traffic for container
if ! sudo iptables -C FORWARD -j RETURN 2> ${redirect} || ! sudo iptables -L FORWARD | awk 'NR==3' | grep RETURN 2> ${redirect}; then
    sudo iptables -I FORWARD -j RETURN
fi

envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} \
    -e NODE_NAME=${NODE_NAME} -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
    -e BUILD_TAG=${BUILD_TAG} -e DEPLOY_TYPE=${DEPLOY_TYPE}"

DOCKER_TAG=`[[ ${BRANCH##*/} == "master" ]] && echo "latest" || echo ${BRANCH##*/}`

FUNCTEST_IMAGE=opnfv/functest-kubernetes:${DOCKER_TAG}
echo "Pulling Docker image ${FUNCTEST_IMAGE} ..."
docker pull ${FUNCTEST_IMAGE}>/dev/null
cmd_opt="run_tests -r -t all"
cmd="docker run --rm --privileged=true ${envs} ${volumes} ${FUNCTEST_IMAGE} /bin/bash -c '${cmd_opt}'"
echo "Running Functest k8s test cases, CMD: ${cmd}"
eval ${cmd}
ret_value=$?
if [ ${ret_value} != 0 ]; then
  echo ${ret_value} > ${ret_val_file}
fi
