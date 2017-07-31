#!/bin/bash
#set -e
[[ $GERRIT_REFSPEC_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"
BOTTLENECKS_IMAGE=opnfv/bottlenecks
REPORT="True"

RELENG_REPO=${WORKSPACE}/releng
[ -d ${RELENG_REPO} ] && rm -rf ${RELENG_REPO}
git clone https://gerrit.opnfv.org/gerrit/releng ${RELENG_REPO} >${redirect}

OPENRC=/tmp/admin_rc.sh

if [[ $SUITE_NAME == *posca* ]]; then
    POSCA_SCRIPT=/home/opnfv/bottlenecks/testsuites/posca

    echo "BOTTLENECKS INFO: fetching os credentials from $INSTALLER_TYPE"
    if [[ $INSTALLER_TYPE == 'compass' ]]; then
        ${RELENG_REPO}/utils/fetch_os_creds.sh -d ${OPENRC} -i ${INSTALLER_TYPE} -a ${INSTALLER_IP} >${redirect}
    fi

    if [[ -f ${OPENRC} ]]; then
        echo "BOTTLENECKS INFO: openstack credentials path is ${OPENRC}"
        cat ${OPENRC}
    else
        echo "BOTTLENECKS ERROR: couldn't find openstack rc file: ${OPENRC}, please check if the it's been properly provided."
        exit 1

    echo "INFO: pulling Bottlenecks docker ${DOCKER_TAG}"
    docker pull opnfv/bottlenecks:${DOCKER_TAG} >$redirect

    opts="--privileged=true -id"
    docker_volume="-v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp"

    cmd="docker run ${opts} --name bottlenecks-load-master ${docker_volume} opnfv/bottlenecks:${DOCKER_TAG} /bin/bash"
    echo "BOTTLENECKS INFO: running docker run commond: ${cmd}"
    ${cmd} >$redirect
    sleep 5

    if [[ $SUITE_NAME == posca_stress_traffic ]]; then
        TEST_CASE=posca_factor_system_bandwidth
        docker exec bottlenecks-load-master python ${POSCA_SCRIPT}/../run_testsuite.py testcase $TEST_CASE $REPORT
    elif [[ $SUITE_NAME == posca_stress_ping ]]; then
        TEST_CASE=posca_factor_ping
        docker exec bottlenecks-load-master python ${POSCA_SCRIPT}/../run_testsuite.py testcase $TEST_CASE $REPORT
    fi

    echo "Bottlenecks: cleaning up docker-compose images and dockers"
    docker-compose -f $WORKSPACE/docker/bottleneck-compose/docker-compose.yml down --rmi all
fi