#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
# log info to console
echo "Starting unit tests for Apex..."
echo "---------------------------------------------------------------------------------------"
echo


pushd ci/ > /dev/null
sudo CONFIG=${CONFIG} LIB=${LIB} ./clean.sh
./test.sh
popd

echo "--------------------------------------------------------"
echo "Unit Tests Done!"
