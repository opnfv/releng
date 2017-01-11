#!/bin/bash
set -e

list_cmd="dovetail list ${TESTSUITE}"
run_cmd="dovetail run --testsuite ${TESTSUITE} -d true"
container_id=$(docker ps -a | grep opnfv/dovetail | awk '{print $1}' | head -1)
docker exec $container_id $list_cmd
docker exec $container_id $run_cmd
