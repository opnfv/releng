#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# delete the $WORKSPACE to open some space
/bin/rm -rf $WORKSPACE
