#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
#test for non-ascii characters, these can pass the test and end up breaking things in production
for x in $(find . -name *\.yml); do

  if LC_ALL=C grep -q '[^[:print:][:space:]]' "$x"; then
    echo "file "$x" contains non-ascii characters"
    exit 1
  fi

done

source /opt/virtualenv/jenkins-job-builder/bin/activate
jenkins-jobs test -o job_output -r jjb/
