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

# Configure the git user/email as we'll be pushing up changes
git config --global user.name "jenkins-ci"
git config --global user.email "jenkins-opnfv-ci@opnfv.org"

# Ensure we are able to generate Commit-IDs for new patchsets
curl -kLo .git/hooks/commit-msg https://gerrit.opnfv.org/gerrit/tools/hooks/commit-msg
chmod +x .git/hooks/commit-msg

# Activate virtualenv, supressing shellcheck warning
# shellcheck source=/dev/null
. $WORKSPACE/venv/bin/activate
pip install -r releases/scripts/requirements.txt

STREAM=${STREAM:-'nostream'}
RELEASE_FILES=$(git diff HEAD^1 --name-only -- "releases/$STREAM")

for release_file in $RELEASE_FILES; do

    while read -r repo branch ref; do

        echo "$repo" "$branch" "$ref"
        branches="$(git ls-remote "https://gerrit.opnfv.org/gerrit/$repo.git" "refs/heads/$branch")"

        if ! [ -z "$branches" ]; then
            echo "refs/heads/$branch already exists at $ref ($branches)"
        else
            ssh -n -f -p 29418 gerrit.opnfv.org gerrit create-branch "$repo" "$branch" "$ref"
        fi

    done < <(python releases/scripts/repos.py -b -f "$release_file")

    python releases/scripts/create_jobs.py -f $release_file
    NEW_FILES=$(git status --porcelain --untracked=no | cut -c4-)
    if [ -n "$NEW_FILES" ]; then
      git add $NEW_FILES
      git commit -sm "Create Stable Branch Jobs for $(basename $release_file .yaml)"
      git push origin HEAD:refs/for/master
    fi
done
