#!/bin/bash
set +e

working_dir=`dirname $0`

branch=${GIT_BRANCH##*/}
[[ "$PUSH_RESULTS_TO_DB" == "true" ]] && flags+="-r"
if [[ ${branch} == *"brahmaputra"* ]]; then
    cmd="${FUNCTEST_REPO_DIR}/docker/run_tests.sh -s ${flags}"
else
    cmd="python ${FUNCTEST_REPO_DIR}/ci/run_tests.py -t all ${flags}"
fi
container_id=$(docker ps -a | grep opnfv/functest | awk '{print $1}' | head -1)
docker exec $container_id $cmd

ret_value=$?
if [[ $ret_value != 0 ]]; then
    # if the daily loop returns error, we still want to push the logs
    # to artifacts repository
    ${working_dir}/../../utils/push-test-logs.sh
fi

