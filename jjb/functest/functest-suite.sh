#!/bin/bash
set -e

echo "Functest: run $FUNCTEST_SUITE_NAME on branch $BRANCH"
if [[ "$BRANCH" =~ 'brahmaputra' ]]; then
    cmd="${FUNCTEST_REPO_DIR}/docker/run_tests.sh --test $FUNCTEST_SUITE_NAME"
elif [[ "$BRANCH" =~ 'colorado' ]]; then
    cmd="python ${FUNCTEST_REPO_DIR}/ci/run_tests.py -t $FUNCTEST_SUITE_NAME"
else
    cmd="functest testcase run $FUNCTEST_SUITE_NAME"
fi
container_id=$(docker ps -a | grep opnfv/functest | awk '{print $1}' | head -1)
docker exec $container_id $cmd

ret_value=$?
ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
echo ${ret_value}>${ret_val_file}

exit 0
