#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -e -o pipefail


GIT_URL=${GIT_URL:-https://gerrit.opnfv.org/gerrit}
STREAM=${STREAM:-'nostream'}
STREAM=fraser
RELEASE_FILES=$(git diff HEAD^1 --name-only -- "releases/$STREAM")
#RELEASE_FILES=$(find releases/fraser/ -type f -name '*.yaml')


#looking for branch
check_branch(){
for release_file in $RELEASE_FILES; do
    while read -r repo branch ref; do
        echo "$repo" "$branch" "$ref"
        unset branch_actual
        branch_actual="$(git ls-remote "https://gerrit.opnfv.org/gerrit/$repo.git" "refs/heads/$branch" | awk '{print $1}')"

        if [ ! -z "$branch_actual" ]; then
            echo "$repo refs/heads/$branch already exists at $branch_actual"
            echo "Therefore this is a tagging job"
            echo "RUN releng-release-create-venv.sh"
            source jjb/releng/releng-release-tagging.sh
        else
            echo "This is a branching job"
            echo "RUN releng-release-create-venv.sh"
            source jjb/releng/releng-release-create-branch.sh
        fi

    done  < <(python releases/scripts/repos.py -b -f "$release_file")
done
}

check_branch
