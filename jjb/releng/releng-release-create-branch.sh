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

# Activate virtualenv, supressing shellcheck warning
# shellcheck source=/dev/null
. $WORKSPACE/venv/bin/activate
pip install -r releases/scripts/requirements.txt

STREAM=${STREAM:-'nostream'}
RELEASE_FILES=$(git diff HEAD^1 --name-only -- "^releases/$STREAM")

for release_file in $RELEASE_FILES; do
    python releases/scripts/create_branch.py -f $release_file
    python releases/scripts/create_jobs.py -f $release_file
    NEW_FILES=$(git status --porcelain --untracked=no | cut -c4-)
    if [ -n "$NEW_FILES" ]; then
      git add $NEW_FILES
      git commit -m "Create Stable Branch Jobs for $(basename $release_file .yaml)"
    fi
done
