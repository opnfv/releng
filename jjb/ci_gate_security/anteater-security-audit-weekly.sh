#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2017 The Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

ANTEATER_SCAN_PATCHSET="${ANTEATER_SCAN_PATCHSET:-true}"

cd $WORKSPACE
REPORTDIR='.reports'
mkdir -p $REPORTDIR
# Ensure any user can read the reports directory
chmod 777 $REPORTDIR

ANTEATER_FILES="--patchset /home/opnfv/anteater/$PROJECT/patchset"

if [[ "$ANTEATER_SCAN_PATCHSET" == "true" ]]; then
    echo "Generating patchset file to list changed files"
    git diff HEAD^1 --name-only | sed "s#^#/home/opnfv/anteater/$PROJECT/#" > $WORKSPACE/patchset
    echo "Changed files are"
    echo "--------------------------------------------------------"
    cat $WORKSPACE/patchset
    echo "--------------------------------------------------------"
else
    echo "Checking full project $PROJECT"
    ANTEATER_FILES="--path /home/opnfv/anteater/$PROJECT"
fi

vols="-v $WORKSPACE:/home/opnfv/anteater/$PROJECT -v $WORKSPACE/$REPORTDIR:/home/opnfv/anteater/$REPORTDIR"
envs="-e PROJECT=$PROJECT"

echo "Pulling releng-anteater docker image"
echo "--------------------------------------------------------"
docker pull opnfv/releng-anteater
echo "--------------------------------------------------------"

cmd="docker run -i $envs $vols --rm opnfv/releng-anteater \
/home/opnfv/venv/bin/anteater --project $PROJECT $ANTEATER_FILES"
echo "Running docker container"
echo "$cmd"
$cmd > $WORKSPACE/securityaudit.log 2>&1
exit_code=$?
echo "--------------------------------------------------------"
echo "Docker container exited with code: $exit_code"
echo "--------------------------------------------------------"
exit 0
