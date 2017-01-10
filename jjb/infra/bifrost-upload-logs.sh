#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 SUSE.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

set -eu
set -o pipefail

BIFROST_CONSOLE_LOG="${BUILD_URL}/consoleText"
BIFROST_GS_URL=${BIFROST_GS_STORAGE/http:/gs:}

echo "Uploading build logs to ${BIFROST_LOG_URL}"

echo "Uploading console output"
curl -L ${BIFROST_CONSOLE_LOG} | gsutil cp - ${BIFROST_GS_URL}/console.txt

[[ ! -d ${WORKSPACE}/logs ]] && exit 0

pushd ${WORKSPACE}/logs/ &> /dev/null
for x in *.log; do
    echo "Compressing and uploading $x"
    tar -czf - $x | gsutil cp - ${BIFROST_GS_URL}/$x.tar.gz
done
popd ${WORKSPACE}/logs &> /dev/null
