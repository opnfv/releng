#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

echo "--------------------------------------------------------"
echo "This is diasy4nfv kolla image build job!"
echo "--------------------------------------------------------"

# start the build
cd $WORKSPACE

# -j is for deciding which branch will be used when building,
# only for OPNFV
./ci/kolla-build.sh -j $JOB_NAME

echo
echo "--------------------------------------------------------"
echo "Done!"
