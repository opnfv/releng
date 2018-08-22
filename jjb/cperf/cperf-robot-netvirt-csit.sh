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
  ODL_STREAM='neon'
else
  ODL_STREAM=${ODL_BRANCH#"stable/"}
fi

echo "ODL Stream set: ${ODL_STREAM} and OS Version is ${FULL_OS_VER}"

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

# Only 1 combo or ctrl node is specified, even for OS HA deployments
# Currently supported combinations are:
# 0cmb-1ctl-2cmp
# 1cmb-0ctl-0cmp
# 1cmb-0ctl-1cmp
if [ "$NUM_COMPUTE_NODES" -eq 0 ]; then
  OPENSTACK_TOPO="1cmb-0ctl-0cmp"
else
  OPENSTACK_TOPO="0cmb-1ctl-2cmp"
fi

idx=1
EXTRA_ROBOT_ARGS=""
for idx in `seq 1 $NUM_CONTROL_NODES`; do
  CONTROLLER_IP=$(python ${REL_PATH}/parse-node-yaml.py get_value -k address --node-number ${idx} --file $NODE_FILE_PATH)
  EXTRA_ROBOT_ARGS+=" -v ODL_SYSTEM_${idx}_IP:${CONTROLLER_IP} \
                      -v OS_CONTROL_NODE_${idx}_IP:${CONTROLLER_IP} \
                      -v ODL_SYSTEM_${idx}_IP:${CONTROLLER_IP} \
                      -v HA_PROXY_${idx}_IP:${SDN_CONTROLLER_IP}"
done

# In all-in-one these Compute IPs still need to be passed to robot
if [ "$NUM_COMPUTE_NODES" -eq 0 ]; then
  EXTRA_ROBOT_ARGS+=" -v OS_COMPUTE_1_IP:'' -v OS_COMPUTE_2_IP:''"
else
  idx=1
  for idx in `seq 1 $NUM_COMPUTE_NODES`; do
    COMPUTE_IP=$(python ${REL_PATH}/parse-node-yaml.py get_value -k address --node-type compute --node-number ${idx} --file $NODE_FILE_PATH)
    EXTRA_ROBOT_ARGS+=" -v OS_COMPUTE_${idx}_IP:${COMPUTE_IP}"
  done
fi

CONTROLLER_1_IP=$(python ${REL_PATH}/parse-node-yaml.py get_value -k address --node-number 1 --file $NODE_FILE_PATH)

if [ "$ODL_CONTAINERIZED" == 'false' ]; then
  EXTRA_ROBOT_ARGS+=" -v NODE_KARAF_COUNT_COMMAND:'ps axf | grep org.apache.karaf | grep -v grep | wc -l || echo 0' \
                      -v NODE_START_COMMAND:'sudo systemctl start opendaylight_api' \
                      -v NODE_KILL_COMMAND:'sudo systemctl stop opendaylight_api' \
                      -v NODE_STOP_COMMAND:'sudo systemctl stop opendaylight_api' \
                      -v NODE_FREEZE_COMMAND:'sudo systemctl stop opendaylight_api' "
else
  EXTRA_ROBOT_ARGS+=" -v NODE_KARAF_COUNT_COMMAND:'sudo docker ps | grep opendaylight_api | wc -l || echo 0' \
                      -v NODE_START_COMMAND:'sudo docker start opendaylight_api' \
                      -v NODE_KILL_COMMAND:'sudo docker stop opendaylight_api' \
                      -v NODE_STOP_COMMAND:'sudo docker stop opendaylight_api' \
                      -v NODE_FREEZE_COMMAND:'sudo docker stop opendaylight_api' "
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
  --name 'CSIT' \
  -e exclude \
  -d $LOGS_LOCATION \
  -v BUNDLEFOLDER:/opt/opendaylight \
  -v CONTROLLER_USER:heat-admin \
  -v DEFAULT_LINUX_PROMPT:\$ \
  -v DEFAULT_LINUX_PROMPT_STRICT:]\$ \
  -v DEFAULT_USER:heat-admin \
  -v DEVSTACK_DEPLOY_PATH:/tmp \
  -v EXTERNAL_GATEWAY:$CONTROLLER_1_IP \
  -v EXTERNAL_PNF:$CONTROLLER_1_IP \
  -v EXTERNAL_SUBNET:192.0.2.0/24 \
  -v EXTERNAL_SUBNET_ALLOCATION_POOL:start=192.0.2.100,end=192.0.2.200 \
  -v EXTERNAL_INTERNET_ADDR:$CONTROLLER_1_IP  \
  -v HA_PROXY_IP:$SDN_CONTROLLER_IP \
  -v NUM_ODL_SYSTEM:$NUM_CONTROL_NODES \
  -v NUM_OS_SYSTEM:$(($NUM_CONTROL_NODES + $NUM_COMPUTE_NODES)) \
  -v NUM_TOOLS_SYSTEM:0 \
  -v ODL_SNAT_MODE:conntrack \
  -v ODL_STREAM:$ODL_STREAM \
  -v ODL_SYSTEM_IP:$CONTROLLER_1_IP \
  -v OS_CONTROL_NODE_IP:$CONTROLLER_1_IP \
  -v OPENSTACK_BRANCH:$FULL_OS_VER \
  -v OPENSTACK_TOPO:$OPENSTACK_TOPO \
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

SUITE_HOME='/home/opnfv/repos/odl_test/csit/suites'

# Disabled suites
#
# ${SUITE_HOME}/openstack/connectivity/live_migration.robot
# Live migration will not work unless we use a shared storage backend like
# Ceph which we do not currently use with CSIT images
#

suites="${SUITE_HOME}/openstack/connectivity/l2.robot \
        ${SUITE_HOME}/openstack/connectivity/l3.robot \
        ${SUITE_HOME}/openstack/connectivity/external_network.robot \
        ${SUITE_HOME}/openstack/connectivity/security_group.robot \
        ${SUITE_HOME}/openstack/securitygroup/neutron_security_group.robot \
        ${SUITE_HOME}/openstack/securitygroup/security_group_l3bcast.robot \
        ${SUITE_HOME}/netvirt/vpnservice/vpn_basic.robot \
        ${SUITE_HOME}/netvirt/vpnservice/vpn_basic_ipv6.robot \
        ${SUITE_HOME}/netvirt/elan/elan.robot \
        ${SUITE_HOME}/netvirt/vpnservice/arp_learning.robot \
        ${SUITE_HOME}/netvirt/l2l3_gatewaymac_arp.robot \
        ${SUITE_HOME}/integration/Create_JVM_Plots.robot"

echo "Robot command set: ${robot_cmd}"
echo "Running robot..."
docker run -i --net=host \
  -v ${LOGS_LOCATION}:${LOGS_LOCATION} \
  -v ${WORKSPACE}/id_rsa:/tmp/id_rsa \
  -v ${WORKSPACE}/overcloudrc:/tmp/overcloudrc \
  opnfv/cperf:$DOCKER_TAG \
  /bin/bash -c "source /tmp/overcloudrc; mkdir -p \$HOME/.ssh; cp /tmp/id_rsa \$HOME/.ssh; \
  cd /home/opnfv/repos/odl_test/ && git pull origin master; \
  yum remove -y python-chardet; \
  pip install odltools; \
  ${robot_cmd} ${suites};"

echo "Running post CSIT clean"
ansible-playbook -i ${CONTROLLER_1_IP}, -u heat-admin --key-file ${WORKSPACE}/id_rsa ${REL_PATH}/csit-clean.yaml.ansible -vvv
