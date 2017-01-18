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
BIFROST_GS_URL=${BIFROST_LOG_URL/http:/gs:}
BIFROST_COMPRESS_SUFFIX="tar.gz"
BIFROST_COMPRESSED_LOGS=()

echo "Uploading build logs to ${BIFROST_LOG_URL}"

echo "Uploading console output"
curl -L ${BIFROST_CONSOLE_LOG} | gsutil cp - ${BIFROST_GS_URL}/build_log.txt

[[ ! -d ${WORKSPACE}/logs ]] && exit 0

pushd ${WORKSPACE}/logs/ &> /dev/null
for x in *.log; do
    echo "Compressing and uploading $x"
    tar -czf - $x | gsutil cp - ${BIFROST_GS_URL}/${x}.${BIFROST_COMPRESS_SUFFIX} 1>/dev/null
    BIFROST_COMPRESSED_LOGS+=(${x}.${BIFROST_COMPRESS_SUFFIX})
done
popd &> /dev/null

echo "Generating the landing page"
cat > index.html << EOF
<html>
<h1>Build results for <a href=https://$GERRIT_NAME/#/c/$GERRIT_CHANGE_NUMBER>$GERRIT_NAME/$GERRIT_CHANGE_NUMBER</h1>
<h2>Job: $JOB_NAME</h2>
<ul>
<li><a href=${BIFROST_LOG_URL}/build_log.txt>build_log.txt</a></li>
EOF

for x in ${BIFROST_COMPRESSED_LOGS[@]}; do
    echo "<li><a href=${BIFROST_LOG_URL}/${x}>${x}</a></li>" >> index.html
done

cat >> index.html << EOF
</ul>
</html>
EOF

gsutil cp index.html ${BIFROST_GS_URL}/index.html
