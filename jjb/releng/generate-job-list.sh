#! /bin/bash
set -o errexit
set -o nounset
set -o pipefail

# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# Job Number Formatter
function JOBS {
    local NUMS=$1
    if [ $NUMS == 1 ]; then
        echo -n "Job"
    else
        echo -n "Jobs"
    fi
}

# We expect job_output to exist prior to this being run and contain the
# output from jenkins-jobs test

echo "> Generating list of previous JJB jobs..."
git checkout -q -b previous-commit HEAD^
jenkins-jobs -l ERROR test -r jjb -o job_output_prev
git checkout -q - && git branch -q -d previous-commit

echo "> Finding job changes ..."
diff -r -q job_output job_output_prev &> job_diff.txt || true

# Only in (job_output) = NEW
# Only in (job_output_prev) = DELETED
# Files ... differ = MODIFIED

declare -a JOBS_ADDED=($(grep 'job_output:' job_diff.txt | cut -d':' -f2- | sed 's/^[ \t]*//;s/[ \t]*$//'))
declare -a JOBS_MODIFIED=($(grep 'differ$' job_diff.txt | sed "s/Files job_output\/\(.*\) and.*/\1/g"))
declare -a JOBS_REMOVED=($(grep 'job_output_prev:' job_diff.txt | cut -d ':' -f2- | sed 's/^[ \t]*//;s/[ \t]*$//'))

NUM_JOBS_ADDED=${#JOBS_ADDED[@]}
NUM_JOBS_MODIFIED=${#JOBS_MODIFIED[@]}
NUM_JOBS_REMOVED=${#JOBS_REMOVED[@]}

echo "> Writing gerrit comment ..."
if [ $NUM_JOBS_ADDED -gt 0 ]; then
    JOB_STRING="$(JOBS $NUM_JOBS_ADDED)"
    { printf "Added %s %s:\n\n" "${NUM_JOBS_ADDED}" "$JOB_STRING";
    printf '* %s\n' "${JOBS_ADDED[@]}";
    printf "\n"; } >> gerrit_comment.txt
fi

if [ $NUM_JOBS_MODIFIED -gt 0 ]; then
    JOB_STRING="$(JOBS $NUM_JOBS_MODIFIED)"
    { printf "Modified %s %s:\n\n" "${NUM_JOBS_MODIFIED}" "$JOB_STRING";
    printf '* %s\n' "${JOBS_MODIFIED[@]}";
    printf "\n"; } >> gerrit_comment.txt
fi

if [ $NUM_JOBS_REMOVED -gt 0 ]; then
    JOB_STRING="$(JOBS $NUM_JOBS_REMOVED)"
    { printf "Removed %s %s:\n\n" "${NUM_JOBS_REMOVED}" "$JOB_STRING";
    printf '* %s\n' "${JOBS_REMOVED[@]}";
    printf "\n"; } >> gerrit_comment.txt
fi
