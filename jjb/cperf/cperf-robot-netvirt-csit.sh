#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

if [ "$OS_VERSION" == 'master' ]; then
  FULL_OS_VER='master'
else
  FULL_OS_VER="stable/${OS_VERSION}"
fi

if [ "$ODL_BRANCH" == 'master' ]; then
  ODL_STREAM='flourine'
else
  ODL_STREAM=${ODL_BRANCH}
fi

echo "ODL Branch set: ${ODL_BRANCH} and OS Version is ${FULL_OS_VER}"

sudo rm -rf releng
git clone https://gerrit.opnfv.org/gerrit/releng.git
REL_PATH='releng/jjb/cperf'

# NOTE: sourcing overcloudrc unsets any variable with OS_ prefix
source ${WORKSPACE}/overcloudrc
# note SDN_CONTROLLER_IP is set in overcloudrc, which is the VIP
# for admin/public network (since we are running single network deployment)

NUM_CONTROL_NODES=$(python ${REL_PATH}/parse-node-yaml.py num_nodes --file $NODE_FILE_PATH)
NUM_COMPUTE_NODES=$(python ${REL_PATH}/parse-node-yaml.py num_nodes --node-type compute --file $NODE_FILE_PATH)

echo "Number of Control nodes found: ${NUM_CONTROL_NODES}"
echo "Number of Compute nodes found: ${NUM_COMPUTE_NODES}"

idx=1
EXTRA_ROBOT_ARGS=""
for idx in `seq 1 $NUM_CONTROL_NODES`; do
  CONTROLLER_IP=$(python ${REL_PATH}/parse-node-yaml.py get_value -k address --node-number ${idx} --file $NODE_FILE_PATH)
  EXTRA_ROBOT_ARGS+=" -v ODL_SYSTEM_${idx}_IP:${CONTROLLER_IP} \
                      -v OS_CONTROL_NODE_${idx}_IP:${CONTROLLER_IP} \
                      -v ODL_SYSTEM_${idx}_IP:${CONTROLLER_IP} \
                      -v HA_PROXY_${idx}_IP:${SDN_CONTROLLER_IP}"
done

idx=1
for idx in `seq 1 $NUM_COMPUTE_NODES`; do
  COMPUTE_IP=$(python ${REL_PATH}/parse-node-yaml.py get_value -k address --node-type compute --node-number ${idx} --file $NODE_FILE_PATH)
  EXTRA_ROBOT_ARGS+=" -v OS_COMPUTE_${idx}_IP:${COMPUTE_IP}"
done

CONTROLLER_1_IP=$(python ${REL_PATH}/parse-node-yaml.py get_value -k address --node-number 1 --file $NODE_FILE_PATH)

if [ "$ODL_CONTAINERIZED" == 'false' ]; then
  EXTRA_ROBOT_ARGS+=" -v NODE_KARAF_COUNT_COMMAND:'ps axf | grep org.apache.karaf | grep -v grep | wc -l || echo 0' \
                      -v NODE_START_COMMAND:'sudo systemctl start opendaylight_api' \
                      -v NODE_KILL_COMMAND:'sudo systemctl stop opendaylight_api' \
                      -v NODE_STOP_COMMAND:'sudo systemctl stop opendaylight_api' \
                      -v NODE_FREEZE_COMMAND:'sudo systemctl stop opendaylight_api' "
else
  EXTRA_ROBOT_ARGS+=" -v NODE_KARAF_COUNT_COMMAND:\"sudo docker exec opendaylight_api /bin/bash -c 'ps axf | \
                                grep org.apache.karaf | grep -v grep | wc -l' || echo 0\" \
                      -v NODE_START_COMMAND:\"sudo docker start opendaylight_api\" \
                      -v NODE_KILL_COMMAND:\"sudo docker stop opendaylight_api\" \
                      -v NODE_STOP_COMMAND:\"sudo docker stop opendaylight_api\" \
                      -v NODE_FREEZE_COMMAND:\"sudo docker stop opendaylight_api\" "
fi

# FIXME(trozet) remove this once it is fixed in csit
# Upload glance image into openstack
wget -O ${WORKSPACE}/cirros-0.3.5-x86_64-disk.img http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img
export ANSIBLE_HOST_KEY_CHECKING=False
ansible-playbook -i ${CONTROLLER_1_IP}, -u heat-admin --key-file ${WORKSPACE}/id_rsa ${REL_PATH}/cirros-upload.yaml.ansible -vvv

LOGS_LOCATION=/tmp/robot_results

robot_cmd="pybot \
  --removekeywords wuks \
  --xunit robotxunit.xml \
  -e exclude \
  -d $LOGS_LOCATION \
  -v BUNDLEFOLDER:/opt/opendaylight \
  -v CONTROLLER_USER:heat-admin \
  -v DEFAULT_LINUX_PROMPT:\$ \
  -v DEFAULT_LINUX_PROMPT_STRICT:]\$ \
  -v DEFAULT_USER:heat-admin \
  -v DEVSTACK_DEPLOY_PATH:/tmp \
  -v HA_PROXY_IP:$SDN_CONTROLLER_IP \
  -v NUM_ODL_SYSTEM:$NUM_CONTROL_NODES \
  -v NUM_OS_SYSTEM:$(($NUM_CONTROL_NODES + $NUM_COMPUTE_NODES)) \
  -v NUM_TOOLS_SYSTEM:0 \
  -v ODL_SNAT_MODE:conntrack \
  -v ODL_STREAM:$ODL_STREAM \
  -v ODL_SYSTEM_IP:$CONTROLLER_1_IP \
  -v OS_CONTROL_NODE_IP:$CONTROLLER_1_IP \
  -v OPENSTACK_BRANCH:$FULL_OS_VER \
  -v OS_USER:heat-admin \
  -v ODL_ENABLE_L3_FWD:yes \
  -v ODL_SYSTEM_USER:heat-admin \
  -v ODL_SYSTEM_PROMPT:\$ \
  -v PRE_CLEAN_OPENSTACK_ALL:True \
  -v PUBLIC_PHYSICAL_NETWORK:datacentre \
  -v RESTCONFPORT:8081 \
  -v ODL_RESTCONF_USER:admin \
  -v ODL_RESTCONF_PASSWORD:$SDN_CONTROLLER_PASSWORD \
  -v KARAF_PROMPT_LOGIN:'opendaylight-user' \
  -v KARAF_PROMPT:'opendaylight-user.*root.*>' \
  -v SECURITY_GROUP_MODE:stateful \
  -v USER:heat-admin \
  -v USER_HOME:\$HOME \
  -v TOOLS_SYSTEM_IP:'' \
  -v NODE_ROLE_INDEX_START:0 \
  -v WORKSPACE:/tmp  \
  $EXTRA_ROBOT_ARGS \
  -v of_port:6653 "

echo "Robot command set: ${robot_cmd}"
echo "Running robot..."
docker run -i --net=host \
  -v ${LOGS_LOCATION}:${LOGS_LOCATION} \
  -v ${WORKSPACE}/id_rsa:/tmp/id_rsa \
  -v ${WORKSPACE}/overcloudrc:/tmp/overcloudrc \
  opnfv/cperf:$DOCKER_TAG \
  /bin/bash -c "source /tmp/overcloudrc; mkdir -p \$HOME/.ssh; cp /tmp/id_rsa \$HOME/.ssh; \
  cd /home/opnfv/repos/odl_test/ && git pull origin master; \
  $robot_cmd /home/opnfv/repos/odl_test/csit/suites/openstack/connectivity/l2.robot;"

UPLOAD_LOCATION=artifacts.opnfv.org/cperf/cperf-apex-csit-${ODL_BRANCH}/${BUILD_NUMBER}/
echo "Uploading robot logs to ${UPLOAD_LOCATION}"
gsutil -m cp -r -v ${LOGS_LOCATION} gs://${UPLOAD_LOCATION} > gsutil.latest_logs.log
