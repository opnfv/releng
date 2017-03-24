#!/bin/bash
##############################################################################
# Copyright (c) 2016 ZTE and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -e

envs="INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP}
-e NODE_NAME=${NODE_NAME} -e CI_DEBUG=${CI_DEBUG}"
ramfs=/tmp/qtip/ramfs
cfg_dir=$(dirname $ramfs)
dir_imgstore="${HOME}/imgstore"
ramfs_volume="$ramfs:/mnt/ramfs"

echo "--------------------------------------------------------"
echo "POD: $NODE_NAME"
echo "INSTALLER: $INSTALLER_TYPE"
echo "Scenario: $DEPLOY_SCENARIO"
echo "--------------------------------------------------------"

echo "Qtip: Pulling docker image: opnfv/qtip:${DOCKER_TAG}"
docker pull opnfv/qtip:$DOCKER_TAG

# use ramfs to fix docker socket connection issue with overlay mode in centos
if [ ! -d $ramfs ]; then
    mkdir -p $ramfs
fi

if [ ! -z "$(df $ramfs | tail -n -1 | grep $ramfs)" ]; then
    sudo mount -t tmpfs -o size=32M tmpfs $ramfs
fi

# enable contro path in docker
cat <<EOF > ${cfg_dir}/ansible.cfg
[defaults]
callback_whitelist = profile_tasks
[ssh_connection]
control_path=/mnt/ramfs/ansible-ssh-%%h-%%p-%%r
EOF

cmd=" docker run -id -e $envs -v ${ramfs_volume} opnfv/qtip:${DOCKER_TAG} /bin/bash"
echo "Qtip: Running docker command: ${cmd}"
${cmd}

container_id=$(docker ps | grep "opnfv/qtip:${DOCKER_TAG}" | awk '{print $1}' | head -1)
if [ $(docker ps | grep 'opnfv/qtip' | wc -l) == 0 ]; then
    echo "The container opnfv/qtip with ID=${container_id} has not been properly started. Exiting..."
    exit 1
else
    echo "The container ID is: ${container_id}"
    QTIP_REPO=/home/opnfv/repos/qtip
    docker cp ${cfg_dir}/ansible.cfg ${container_id}:/home/opnfv/.ansible.cfg
# TODO(zhihui_wu): use qtip cli to execute benchmark test in the future
    docker exec -t ${container_id} bash -c "cd ${QTIP_REPO}/qtip/runner/ &&
    python runner.py -d /home/opnfv/qtip/results/ -b all"

fi

echo "Qtip done!"
