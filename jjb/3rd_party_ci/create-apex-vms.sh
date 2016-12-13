#!/bin/bash
set -e
. ./odl-pipeline-common.sh
pushd $LIB
  ./test_environment.sh --env-number $APEX_ENV_NUMBER --cloner-info $CLONER_INFO --snapshot-disks $SNAPSHOT_DISKS
popd