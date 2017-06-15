#!/bin/bash
set -o errexit
set -o pipefail
export PATH=$PATH:/usr/local/bin/

declare -a PROJECT_LIST
EXCLUDE_PROJECTS="All-Projects|All-Users"
CLONE_PATH="$WORKSPACE/opnfv-archive"

# Generate project list from gerrit
PROJECT_LIST=($(ssh -p 29418 gerrit.opnfv.org gerrit ls-projects | egrep -v $EXCLUDE_PROJECTS))

for PROJECT in ${PROJECT_LIST[@]}; do
  echo "> Cloning $PROJECT"
  if [ ! -d "$CLONE_PATH/$PROJECT" ]; then
    git clone "https://gerrit.opnfv.org/gerrit/$PROJECT.git" $CLONE_PATH/$PROJECT

    # Don't license scan kernel or qemu
    if [ "$PROJECT" == "kvmfornfv" ]; then
      rm -rf $CLONE_PATH/$PROJECT/{kernel,qemu}
    fi
  else
    git --work-tree="$CLONE_PATH/$PROJECT" pull -f
  fi
done

# Clear git data
find $CLONE_PATH -type d -iname '.git' -exec rm -rf {} +
find $CLONE_PATH -type f -iname '.git*' -exec rm -rf {} +

# Create archive
cd $WORKSPACE
tar -czf opnfv-archive.tar.gz opnfv-archive

