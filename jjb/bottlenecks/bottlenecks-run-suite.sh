#!/bin/bash
#set -e
[[ $GERRIT_REFSPEC_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"
BOTTLENECKS_IMAGE=opnfv/bottlenecks
REPORT="True"

if [[ $SUITE_NAME == rubbos || $SUITE_NAME == vstf ]]; then
    echo "Bottlenecks: to pull image $BOTTLENECKS_IMAGE:${DOCKER_TAG}"
    docker pull $BOTTLENECKS_IMAGE:$DOCKER_TAG >${redirect}

    echo "Bottlenecks: docker start running"
    opts="--privileged=true -id"
    envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP} \
          -e NODE_NAME=${NODE_NAME} -e EXTERNAL_NET=${EXTERNAL_NETWORK} \
          -e BOTTLENECKS_BRANCH=${BOTTLENECKS_BRANCH} -e GERRIT_REFSPEC_DEBUG=${GERRIT_REFSPEC_DEBUG} \
          -e BOTTLENECKS_DB_TARGET=${BOTTLENECKS_DB_TARGET} -e PACKAGE_URL=${PACKAGE_URL}"
    cmd="sudo docker run ${opts} ${envs} $BOTTLENECKS_IMAGE:${DOCKER_TAG} /bin/bash"
    echo "Bottlenecks: docker cmd running ${cmd}"
    ${cmd} >${redirect}

    echo "Bottlenecks: obtain docker id"
    container_id=$(docker ps | grep "$BOTTLENECKS_IMAGE:${DOCKER_TAG}" | awk '{print $1}' | head -1)
    if [ -z ${container_id} ]; then
        echo "Cannot find $BOTTLENECKS_IMAGE container ID ${container_id}. Please check if it exists."
        docker ps -a
        exit 1
    fi

    echo "Bottlenecks: to prepare openstack environment"
    prepare_env="${REPO_DIR}/ci/prepare_env.sh"
    echo "Bottlenecks: docker cmd running: ${prepare_env}"
    sudo docker exec ${container_id} ${prepare_env}

    echo "Bottlenecks: to run testsuite ${SUITE_NAME}"
    run_testsuite="${REPO_DIR}/run_tests.sh -s ${SUITE_NAME}"
    echo "Bottlenecks: docker cmd running: ${run_testsuite}"
    sudo docker exec ${container_id} ${run_testsuite}
else
    echo "Bottlenecks: installing POSCA docker-compose"
    if [ -d usr/local/bin/docker-compose ]; then
        rm -rf usr/local/bin/docker-compose
    fi
    curl -L https://github.com/docker/compose/releases/download/1.11.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    echo "Bottlenecks: composing up dockers"
    cd $WORKSPACE
    docker-compose -f $WORKSPACE/docker/bottleneck-compose/docker-compose.yml up -d

    echo "Bottlenecks: running traffic stress/factor testing in posca testsuite "
    POSCA_SCRIPT=/home/opnfv/bottlenecks/testsuites/posca
    if [[ $SUITE_NAME == posca_stress_traffic ]]; then
        TEST_CASE=posca_factor_system_bandwidth
        echo "Bottlenecks: pulling tutum/influxdb for yardstick"
        docker pull tutum/influxdb:0.13
        sleep 5
        docker exec bottleneckcompose_bottlenecks_1 python ${POSCA_SCRIPT}/run_posca.py testcase $TEST_CASE $REPORT
    elif [[ $SUITE_NAME == posca_stress_ping ]]; then
        TEST_CASE=posca_factor_ping
        sleep 5
        docker exec bottleneckcompose_bottlenecks_1 python ${POSCA_SCRIPT}/run_posca.py testcase $TEST_CASE $REPORT
    fi

    echo "Bottlenecks: cleaning up docker-compose images and dockers"
    docker-compose -f $WORKSPACE/docker/bottleneck-compose/docker-compose.yml down --rmi all
fi