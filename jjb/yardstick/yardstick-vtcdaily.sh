#!/bin/bash
set -e
[[ $CI_DEBUG == true ]] && redirect="/dev/stdout" || redirect="/dev/null"

cd $WORKSPACE
./tests/ci/apexlake-verify
