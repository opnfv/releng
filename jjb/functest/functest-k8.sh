#!/bin/bash

set -e
set +u
set +o pipefail

redirect="/dev/stdout"
FUNCTEST_DIR=/home/opnfv/functest

admin_conf_file_vol="-v ${HOME}/admin.conf:/root/.kube/config"
cat ${HOME}/admin.conf

dir_result="${HOME}/opnfv/functest/results/${BRANCH##*/}"
mkdir -p ${dir_result}
sudo rm -rf ${dir_result}/*
results_vol="-v ${dir_result}:${FUNCTEST_DIR}/results"

volumes="${results_vol} ${admin_conf_file_vol}"

envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} \
    -e NODE_NAME=${NODE_NAME} -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
    -e BUILD_TAG=${BUILD_TAG}"

DOCKER_TAG=${DOCKER_TAG:-$([[ ${BRANCH##*/} == "master" ]] && echo "latest" || echo ${BRANCH##*/})}

set +e

ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
echo 0 > ${ret_val_file}

FUNCTEST_IMAGES="\
opnfv/functest-kubernetes-healthcheck:${DOCKER_TAG} \
opnfv/functest-kubernetes-smoke:${DOCKER_TAG}"
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
