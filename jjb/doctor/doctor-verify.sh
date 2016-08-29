#!/bin/bash

echo "/home/jenkins/pod_info :"
sed -e 's/^/    /' /home/jenkins/pod_info
echo
source /home/jenkins/pod_info

sudo docker pull opnfv/functest:master
sudo docker run --privileged=true -id \
    -e INSTALLER_TYPE=${INSTALLER_TYPE} \
    -e INSTALLER_IP=${INSTALLER_IP} \
    -e NODE_NAME=${NODE_NAME} \
    -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
    -e BUILD_TAG=${BUILD_TAG} \
    -e CI_DEBUG=true \
    -v ${SSH_KEY}:/root/.ssh/id_rsa \
    -v ${WORKSPACE}:/home/opnfv/repos/doctor \
    -v ${OS_CREDS}:/home/opnfv/functest/conf/openstack.creds \
    opnfv/functest:master /bin/bash
sleep 5

container_id=$(sudo docker ps | awk '/opnfv/{print $1}' | head -1)
sudo docker exec ${container_id} python /home/opnfv/repos/functest/ci/prepare_env.py start
sudo docker exec ${container_id} python /home/opnfv/repos/functest/ci/run_tests.py -t doctor
sudo docker kill ${container_id}
