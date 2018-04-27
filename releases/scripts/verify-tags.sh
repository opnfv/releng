#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
TAG=opnfv-6.0.0

virtualenv tagging
# shellcheck source=/dev/null
source tagging/bin/activate
pip install -r releases/scripts/requirements.txt > /dev/null

rm repos.txt
for project in releases/fraser/*; do
    echo "---> Verify tags for $project"
    python releases/scripts/repos.py -r $TAG -f $project | tee -a repos.txt
done

echo "---> Tags verified"
