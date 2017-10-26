#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

echo "--------------------------------------------------------"
echo "This is diasy4nfv kolla image build job!"
echo "--------------------------------------------------------"

# start the build
cd $WORKSPACE
./ci/kolla-build.sh

echo
echo "--------------------------------------------------------"
echo "Done!"
