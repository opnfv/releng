#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# delete everything that is in $WORKSPACE
sudo /bin/rm -rf $WORKSPACE
