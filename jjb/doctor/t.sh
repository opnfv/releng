#!/bin/bash
set -e
set -o pipefail


[[ $GERRIT_CHANGE_NUMBER =~ .* ]]


echo "done"
