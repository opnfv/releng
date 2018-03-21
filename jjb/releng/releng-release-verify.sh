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
RELEASE_FILES=$(git diff HEAD^1 --name-only -- "releases/$STREAM")

# TODO: The create_branch.py should be refactored so it can be used here
# to verify the commit exists that is being added, along with
# jjb/<project>
for release_file in $RELEASE_FILES; do
    python releases/scripts/verify_schema.py \
    -s releases/schema.yaml \
    -y $release_file
done
