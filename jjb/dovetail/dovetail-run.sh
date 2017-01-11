#!/bin/bash
set -e

list_cmd="dovetail list ${TESTSUITE}"
run_cmd="dovetail run --testsuite ${TESTSUITE} -d true"
container_id=$(docker ps -a | grep opnfv/dovetail | awk '{print $1}' | head -1)
echo "Container exec command: ${list_cmd}"
docker exec $container_id ${list_cmd}
echo "Container exec command: ${run_cmd}"
docker exec $container_id ${run_cmd}

sudo cp -r ${DOVETAIL_REPO_DIR}/results ./
#To make sure the file owner is jenkins, for the copied results files in the above line
#if not, there will be error when next time to wipe workspace
sudo chown -R jenkins:jenkins ${WORKSPACE}/results

echo "Dovetail: done!"
