#!/bin/bash

set -eu
set -o pipefail

BIFROST_CONSOLE_LOG="${BUILD_URL}/consoleText"

echo "Uploading build logs to ${BIFROST_LOG_URL}"

curl -L ${BIFROST_CONSOLE_LOG} | gsutil cp - ${BIFROST_GS_STORAGE/http:/gs:}/console.txt
