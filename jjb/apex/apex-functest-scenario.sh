#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

features=$(echo $DEPLOY_SCENARIO | sed -r -n 's/os-.+-(.+)-(noha|ha)/\1/p')
if [ "$features" == 'rocky' ]; then
  functest_scenario=$(echo $DEPLOY_SCENARIO | sed -r -n 's/(os-.+?)-rocky-(noha|ha)/\1-nofeature-\2/p')
  echo "DOCKER_TAG=hunter" > functest_scenario
elif [[ "$features" =~ 'rocky' ]]; then
  functest_scenario=$(echo $DEPLOY_SCENARIO | sed -r -n 's/(os-.+?)-(.+)_rocky-(noha|ha)/\1-\2-\3/p')
  echo "DOCKER_TAG=hunter" > functest_scenario
else
  functest_scenario=$(echo $DEPLOY_SCENARIO | sed -r -n 's/-(noha|ha).*/-\1/p')
  echo "DOCKER_TAG=$([[ ${BRANCH##*/} == "master" ]] && \
    echo "latest" || echo ${BRANCH##*/})" > functest_scenario
fi
echo "DEPLOY_SCENARIO=$functest_scenario" >> functest_scenario
