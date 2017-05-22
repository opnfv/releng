#!/bin/bash
##############################################################################
# Copyright (c) 2017 ZTE and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -e

echo "--------------------------------------------------------"
echo "POD: $NODE_NAME"
echo "Scenario: $DEPLOY_SCENARIO"
echo "INSTALLER: $INSTALLER_TYPE"
echo "INSTALLER_IP: $INSTALLER_IP"
echo "--------------------------------------------------------"

echo "Qtip: Pulling docker image: opnfv/qtip:${DOCKER_TAG}"
docker pull opnfv/qtip:$DOCKER_TAG >/dev/null

envs="INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP}
-e POD_NAME=${NODE_NAME} -e SCENARIO=${DEPLOY_SCENARIO}"

cmd=" docker run -id -e $envs opnfv/qtip:${DOCKER_TAG} /bin/bash"
echo "Qtip: Running docker command: ${cmd}"
${cmd}

container_id=$(docker ps | grep "opnfv/qtip:${DOCKER_TAG}" | awk '{print $1}' | head -1)
if [ $(docker ps | grep 'opnfv/qtip' | wc -l) == 0 ]; then
    echo "The container opnfv/qtip with ID=${container_id} has not been properly started. Exiting..."
    exit 1
fi

echo "The container ID is: ${container_id}"
QTIP_REPO=/home/opnfv/repos/qtip

docker exec -t ${container_id} bash -c "bash ${QTIP_REPO}/tests/ci/run_ci.sh"

echo "Qtip done!"
exit 0