#!/bin/bash
set +e

[[ "$PUSH_RESULTS_TO_DB" == "true" ]] && flags+="-r"
cmd="run_tests -t all ${flags}"

container_id=$(docker ps -a | grep opnfv/functest | awk '{print $1}' | head -1)
docker exec $container_id $cmd

ret_value=$?
ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
echo ${ret_value}>${ret_val_file}

exit 0
