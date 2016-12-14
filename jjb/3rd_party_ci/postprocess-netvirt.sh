#!/bin/bash
set -e

# wipe the WORKSPACE
if [ -z ${WORKSPACE} ]; then echo "WORKSPACE is unset"; else echo "WORKSPACE is set to \"$WORKSPACE\""; fi
WORKSPACE=${WORKSPACE:-$PWD}
/bin/rm -rf $WORKSPACE/*

# clone opnfv sdnvpn repo
git clone https://gerrit.opnfv.org/gerrit/p/sdnvpn.git $WORKSPACE/sdnvpn
. $WORKSPACE/sdnvpn/odl-pipeline/odl-pipeline-common.sh
pushd $LIB
./postprocess.sh
popd
