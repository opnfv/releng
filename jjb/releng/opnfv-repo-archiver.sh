#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o pipefail
export PATH=$PATH:/usr/local/bin/

DATE="$(date +%Y%m%d)"

declare -a PROJECT_LIST
EXCLUDE_PROJECTS="All-Projects|All-Users|securedlab"
CLONE_PATH="$WORKSPACE/opnfv-repos"

# Generate project list from gerrit
PROJECT_LIST=($(ssh -p 29418 jenkins-ci@gerrit.opnfv.org gerrit ls-projects | egrep -v $EXCLUDE_PROJECTS))

echo "Cloning all OPNFV repositories"
echo "------------------------------"

for PROJECT in "${PROJECT_LIST[@]}"; do
  echo "> Cloning $PROJECT"
  if [ ! -d "$CLONE_PATH/$PROJECT" ]; then
    git clone "https://gerrit.opnfv.org/gerrit/$PROJECT.git" $CLONE_PATH/$PROJECT
  else
    pushd "$CLONE_PATH/$PROJECT" &>/dev/null
    git pull -f
    popd &> /dev/null
  fi

  # Don't license scan kernel or qemu in kvmfornfv
  if [ "$PROJECT" == "kvmfornfv" ]; then
    rm -rf "$CLONE_PATH/$PROJECT/{kernel,qemu}"
  fi
done

echo "Finished cloning OPNFV repositories"
echo "-----------------------------------"

# Copy repos and clear git data
echo "Copying repos to $WORKSPACE/opnfv-archive and removing .git files"
cp -R $CLONE_PATH $WORKSPACE/opnfv-archive
find $WORKSPACE/opnfv-archive -type d -iname '.git' -exec rm -rf {} +
find $WORKSPACE/opnfv-archive -type f -iname '.git*' -exec rm -rf {} +

# Create archive
echo "Creating archive: opnfv-archive-$DATE.tar.gz"
echo "--------------------------------------"
cd $WORKSPACE
tar -czf "opnfv-archive-$DATE.tar.gz" opnfv-archive && rm -rf opnfv-archive
echo "Archiving Complete."

echo "Uploading artifacts"
echo "--------------------------------------"

gsutil cp "$WORKSPACE/opnfv-archive-$DATE.tar.gz" \
    "gs://opnfv-archive/opnfv-archive-$DATE.tar.gz" 2>&1

rm -f opnfv-archive-$DATE.tar.gz

echo "Finished"
