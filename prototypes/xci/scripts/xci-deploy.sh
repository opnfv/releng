#!/bin/bash
set -eux
set -o errexit
set -o nounset
set -o pipefail

# find where are we
XCI_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# source pinned versions
source $XCI_PATH/pinned-versions

# source user vars
source $XCI_PATH/user-vars

# source flavor configuration
source $XCI_PATH/../flavors/$XCI_FLAVOR.sh
