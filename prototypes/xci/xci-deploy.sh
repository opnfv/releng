#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# find where are we
XCI_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# source pinned versions
source $XCI_PATH/config/pinned-versions

# source user vars
source $XCI_PATH/config/user-vars

# source flavor configuration
source $XCI_PATH/flavors/$XCI_FLAVOR.sh
