#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o pipefail

TAG="${TAG:-opnfv-6.0.0}"
RELEASE="${RELEASE:-fraser}"

[ -a repos.txt ] && rm repos.txt

for project in releases/$RELEASE/*; do
    python releases/scripts/repos.py -n -f $project >> repos.txt
done

while read -r repo
do
    tag="$(git ls-remote "https://gerrit.opnfv.org/gerrit/$repo.git" "refs/tags/$TAG")"
    echo "$repo $tag"
done < repos.txt
