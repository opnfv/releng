#!/bin/bash
set -o errexit
set -o pipefail
export PATH=$PATH:/usr/local/bin/

declare -a PROJECT_LIST
EXCLUDE_PROJECTS="All-Projects|All-Users"

PROJECT_LIST=($(ssh gerrit.opnfv.org gerrit ls-projects | egrep -v $EXCLUDE_PROJECTS))
echo "PROJECT_LIST=(${PROJECT_LIST[*]})" > opnfv-projects.sh

for PROJECT in ${PROJECT_LIST[@]}; do
  echo "> Cloning $PROJECT"
  if [ ! -d "$PROJECT" ]; then
    git clone "https://gerrit.opnfv.org/gerrit/$PROJECT.git"
  else
    pushd "$PROJECT" > /dev/null
    git pull -f
    popd > /dev/null
  fi
done
