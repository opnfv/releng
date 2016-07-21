#!/bin/bash
# SPDX-license-identifier: Apache-2.0
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
res_build_date=${1:-$(date -u +"%Y-%m-%d_%H-%M-%S")}
project=$PROJECT
branch=${GIT_BRANCH##*/}
testbed=$NODE_NAME
dir_result="${HOME}/opnfv/$project/results/${branch}"
# src: https://wiki.opnfv.org/display/INF/Hardware+Infrastructure
# + intel-pod3 (vsperf)
node_list=(\
'lf-pod1' 'lf-pod2' 'intel-pod2' 'intel-pod3' \
'intel-pod5' 'intel-pod6' 'intel-pod7' 'intel-pod8' \
'ericsson-pod2' \
'huawei-pod1' 'huawei-pod2' 'huawei-virtual1' 'huawei-virtual2' 'huawei-virtual3' 'huawei-virtual4')


if [[ ! " ${node_list[@]} " =~ " ${testbed} " ]]; then
    echo "This is not a CI POD. Aborting pushing the logs to artifacts."
    exit 0
fi

if [[ "$branch" == "master" ]]; then
    project_artifact=logs/$project/$testbed/$res_build_date
else
    project_artifact=logs/$project/$testbed/$branch/$res_build_date
fi

# create the folder to store the results
mkdir -p $dir_result

# copy folder to artifact
if [ -d "$dir_result" ]; then
    if [ "$(ls -A $dir_result)" ]; then
        set +e
        gsutil&>/dev/null
        if [ $? != 0 ]; then
            echo "Not possible to push results to artifact: gsutil not installed";
        else
            gsutil ls gs://artifacts.opnfv.org/"$project"/ &>/dev/null
            if [ $? != 0 ]; then
                echo "Not possible to push results to artifact: gsutil not installed.";
            else
                echo "copy result files to artifact $project_artifact"
                gsutil -m cp -r "$dir_result" gs://artifacts.opnfv.org/"$project_artifact"/
            fi
        fi
    else
          echo "Result folder is empty"
    fi
fi
