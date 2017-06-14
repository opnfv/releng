#!/bin/bash
# SPDX-license-identifier: Apache-2.0
set -o errexit
set -o pipefail
set -o nounset
export PATH=$PATH:/usr/local/bin/


#WORKSPACE="$(pwd)"

cd $WORKSPACE
if [ ! -d "$WORKSPACE/allrepos" ]; then
  mkdir $WORKSPACE/allrepos
fi

cd $WORKSPACE/allrepos

declare -a PROJECT_LIST
EXCLUDE_PROJECTS="All-Projects|All-Users|securedlab"

PROJECT_LIST=($(ssh gerrit.opnfv.org -p 29418 gerrit ls-projects | egrep -v $EXCLUDE_PROJECTS))
echo "PROJECT_LIST=(${PROJECT_LIST[*]})" > $WORKSPACE/opnfv-projects.sh

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
