#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# delete everything that is in $WORKSPACE
/bin/rm -rf $WORKSPACE