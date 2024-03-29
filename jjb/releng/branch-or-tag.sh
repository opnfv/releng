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
set -x

GIT_URL=${GIT_URL:-https://gerrit.opnfv.org/gerrit}
STREAM=${STREAM:-'nostream'}
RELEASE_FILES=$(git diff HEAD^1 --name-only -- "releases/$STREAM")

echo "--> Verifying $RELEASE_FILES."
for release_file in $RELEASE_FILES; do
    # Verify the release file schema
    python3 releases/scripts/verify_schema.py \
    -s releases/schema.yaml \
    -y $release_file
done

for release_file in $RELEASE_FILES; do
    while read -r repo branch ref; do
        echo "$repo" "$branch" "$ref"
        unset branch_actual
        branch_actual="$(git ls-remote "https://gerrit.opnfv.org/gerrit/$repo.git" "refs/heads/$branch" | awk '{print $1}')"

        if [ -n "$branch_actual" ]; then
            echo "$repo refs/heads/$branch already exists at $branch_actual"
            source jjb/releng/releng-release-tagging.sh
        else
            echo "This is a branching job"
            source jjb/releng/releng-release-create-branch.sh
        fi

    done  < <(python3 releases/scripts/repos.py -b -f "$release_file")
done
