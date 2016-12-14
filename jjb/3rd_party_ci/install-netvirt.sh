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
./odl_reinstaller.sh --cloner-info $CLONER_INFO --odl-artifact $NETVIRT_ARTIFACT
popd