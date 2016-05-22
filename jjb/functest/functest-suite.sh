#!/bin/bash
set -e

branch=${GIT_BRANCH##*/}
echo "Functest: run $FUNCTEST_SUITE_NAME on branch ${branch}"
if [[ ${branch} == *"brahmaputra"* ]]; then
    cmd="${FUNCTEST_REPO_DIR}/docker/run_tests.sh --test $FUNCTEST_SUITE_NAME"
else
    cmd="python ${FUNCTEST_REPO_DIR}/ci/run_tests.py -t $FUNCTEST_SUITE_NAME"
fi
container_id=$(docker ps -a | grep opnfv/functest | awk '{print $1}' | head -1)
docker exec $container_id $cmd
