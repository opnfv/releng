#!/bin/bash
set -e
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

cd $WORKSPACE
./ci/apexlake-verify
