#!/bin/bash
set -e

sshpass -p root ssh root@10.1.0.50 \
  "mkdir -p /etc/yardstick; rm -rf /etc/yardstick/admin.conf"


sshpass -p root ssh root@10.1.0.50 \
  kubectl config set-cluster yardstick --server=127.0.0.1:8080 --insecure-skip-tls-verify=true --kubeconfig=/etc/yardstick/admin.conf
sshpass -p root ssh root@10.1.0.50 \
  kubectl config set-context yardstick --cluster=yardstick --kubeconfig=/etc/yardstick/admin.conf
sshpass -p root ssh root@10.1.0.50 \
  kubectl config use-context yardstick --kubeconfig=/etc/yardstick/admin.conf 



if [ ! -n "$redirect" ]; then
  redirect="/dev/stdout"
fi

if [ ! -n "$DOCKER_TAG" ]; then
  DOCKER_TAG='latest'
fi

if [ ! -n "$NODE_NAME" ]; then
  NODE_NAME='arm-virutal03'
fi

if [ ! -n "$DEPLOY_SCENARIO" ]; then
  DEPLOY_SCENARIO='k8-nosdn-lb-noha_daily'
fi

if [ ! -n "$YARDSTICK_DB_BACKEND" ]; then
  YARDSTICK_DB_BACKEND='-i 104.197.68.199:8086'
fi

# Pull the image with correct tag
DOCKER_REPO='opnfv/yardstick'
if [ "$(uname -m)" = 'aarch64' ]; then
    DOCKER_REPO="${DOCKER_REPO}_$(uname -m)"
fi
echo "Yardstick: Pulling image ${DOCKER_REPO}:${DOCKER_TAG}"
sshpass -p root ssh root@10.1.0.50 \
  docker pull ${DOCKER_REPO}:$DOCKER_TAG >$redirect

if [ ! -n "$BRANCH" ]; then
  BRANCH=master
fi

opts="--name=yardstick --privileged=true --net=host -d -it "
envs="-e YARDSTICK_BRANCH=${BRANCH} -e BRANCH=${BRANCH} \
  -e NODE_NAME=${NODE_NAME} \
  -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO}"
rc_file_vol="-v /etc/yardstick/admin.conf:/etc/yardstick/admin.conf"
cacert_file_vol=""
map_log_dir=""
sshkey=""
YARDSTICK_SCENARIO_SUITE_NAME="opnfv_k8-nosdn-lb-noha_daily.yaml"

# map log directory
branch=${BRANCH##*/}
#branch="master"
dir_result="${HOME}/opnfv/yardstick/results/${branch}"
mkdir -p ${dir_result}
sudo rm -rf ${dir_result}/*
map_log_dir="-v ${dir_result}:/tmp/yardstick"

# Run docker
cmd="docker rm -f yardstick || true"
sshpass -p root ssh root@10.1.0.50 \
  ${cmd}

cmd="sudo docker run ${opts} ${envs} ${rc_file_vol} ${cacert_file_vol} ${map_log_dir} ${sshkey} ${DOCKER_REPO}:${DOCKER_TAG} /bin/bash"
echo "Yardstick: Running docker cmd: ${cmd}"
sshpass -p root ssh root@10.1.0.50 \
  ${cmd}


cmd='sudo docker exec yardstick sed -i.bak "/# execute tests/i\sed -i.bak \"s/openretriever\\\/yardstick/openretriever\\\/yardstick_aarch64/g\" \
    $\{YARDSTICK_REPO_DIR\}/tests/opnfv/test_cases/opnfv_yardstick_tc080.yaml" /usr/local/bin/exec_tests.sh'
sshpass -p root ssh root@10.1.0.50 \
  ${cmd}

echo "Replace the X86 libzmq shared object file to that of aarch64"
cmd='sudo docker exec yardstick bash -c "if [  -f /opt/nsb_bin/trex/scripts/external_libs/pyzmq-14.5.0/python2/ucs4/64bit/zmq/libzmq.so.3 ]; then  cp /usr/lib/aarch64-linux-gnu/libzmq.so /opt/nsb_bin/trex/scripts/external_libs/pyzmq-14.5.0/python2/ucs4/64bit/zmq/libzmq.so.3; fi"'
sshpass -p root ssh root@10.1.0.50 \
  ${cmd}

echo "Yardstick: run tests: ${YARDSTICK_SCENARIO_SUITE_NAME}"
cmd="sudo docker exec yardstick exec_tests.sh ${YARDSTICK_DB_BACKEND} ${YARDSTICK_SCENARIO_SUITE_NAME}"
sshpass -p root ssh root@10.1.0.50 \
  ${cmd}

cmd="docker rm -f yardstick"
sshpass -p root ssh root@10.1.0.50 \
  ${cmd}

echo "Yardstick: done!"
