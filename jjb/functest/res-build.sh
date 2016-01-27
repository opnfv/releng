#!/bin/bash
# @License Apache-2.0 <http://spdx.org/licenses/Apache-2.0>
##############################################################################
# Copyright (c) 2016 Orange and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -e
set -o pipefail

export PATH=$PATH:/usr/local/bin/

git_sha1="$(git rev-parse HEAD)"
res_build_date=$(date -u +"%Y-%m-%d_%H-%M-%S")

# Result directory in the jumphost
# to be used only with CI
dir_result="${HOME}/opnfv/functest/results"

# Clean the results directory
# remove json file for rally, export only html
# json should have been pushed into the DB
rm -f $dir_result/rally/*.json

# Several information are required: date and testbed
# date is generated by functest so on the artifact, the results shall be under functest/<testbed id>/date/
testbed=$NODE_NAME

project_artifact=logs/functest/$testbed/$res_build_date

# copy folder to artifact
if [ -d "$dir_result" ]; then
    if [ "$(ls -A $dir_result)" ]; then
          echo "copy result files to artifact $project_artifact"
          gsutil -m cp -r "$dir_result" gs://artifacts.opnfv.org/"$project_artifact"/

          # delete local results
          # should not be useful as the container is about to die...just in case
          rm -Rf /home/opnfv/functest/results/*
    else
          echo "Result folder is empty"
    fi
else
    echo "No result folder found"
fi
