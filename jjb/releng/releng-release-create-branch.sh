#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -xe

GIT_URL=${GIT_URL:-https://gerrit.opnfv.org/gerrit}
STREAM=${STREAM:-'nostream'}
RELEASE_FILES=$(git diff HEAD^1 --name-only -- "releases/$STREAM")

# Configure the git user/email as we'll be pushing up changes
git config --global user.name "fbot"
git config --global user.email "jenkins-opnfv-ci@opnfv.org"

# Ensure we are able to generate Commit-IDs for new patchsets
curl -kLo .git/hooks/commit-msg https://gerrit.opnfv.org/gerrit/tools/hooks/commit-msg
chmod +x .git/hooks/commit-msg

clone_repo(){
echo "--> Cloning $repo"
if [ ! -d $repo ]; then
    git clone $GIT_URL/$repo.git $repo
fi
}

check_if_ref_exists(){
clone_repo
cd "$repo"
if git rev-list refs/heads/master | grep "$ref"; then
  echo "$ref exists"
  REF_EXISTS=true
  cd -
else
  echo "$ref Does not exist please submit a valid ref for branching"
  exit 1
fi
}

run_merge(){
unset NEW_FILES
if [[ $REF_EXISTS = true && "$JOB_NAME" =~ "merge" ]]; then
  ssh -o 'PubkeyAcceptedKeyTypes +ssh-rsa' -n -f -p 29418 fbot@gerrit.opnfv.org gerrit create-branch "$repo" "$branch" "$ref"
  python3 releases/scripts/create_jobs.py -f $release_file
  NEW_FILES=$(git status --porcelain --untracked=no | cut -c4-)
fi
if [ -n "$NEW_FILES" ]; then
  git add $NEW_FILES
  git commit -sm "Create Stable Branch Jobs for $(basename $release_file .yaml)"
  git push origin HEAD:refs/for/master
fi
}

main(){
for release_file in $RELEASE_FILES; do
    while read -r repo branch ref; do
        echo "$repo" "$branch" "$ref"
        branches="$(git ls-remote "https://gerrit.opnfv.org/gerrit/$repo.git" "refs/heads/$branch")"
        if ! [ -z "$branches" ]; then
            echo "refs/heads/$branch already exists at $ref ($branches)"
        else
            run_merge
        fi
    done < <(python3 releases/scripts/repos.py -b -f "$release_file")
done
}

check_if_ref_exists
main
