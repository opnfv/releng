#!/bin/bash
set -e

if [ -z ${WORKSPACE} ]; then
  echo "WORKSPACE is unset. Please do so."
fi
# wipe the WORKSPACE
/bin/rm -rf $WORKSPACE/*
# clone opnfv sdnvpn repo
git clone https://gerrit.opnfv.org/gerrit/p/sdnvpn.git $WORKSPACE/sdnvpn

. $WORKSPACE/sdnvpn/odl-pipeline/odl-pipeline-common.sh
pushd $LIB
./test_environment.sh --env-number $APEX_ENV_NUMBER --cloner-info $CLONER_INFO --snapshot-disks $SNAPSHOT_DISKS --vjump-hosts $VIRTUAL_JUMPHOSTS
popd
