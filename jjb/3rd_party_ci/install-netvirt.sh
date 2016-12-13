#!/bin/bash
set -e
# clone opnfv sdnvpn repo
git clone https://gerrit.opnfv.org/gerrit/p/sdnvpn.git $WORKSPACE/sdnvpn
. $WORKSPACE/sdnvpn/odl-pipeline/odl-pipeline-common.sh
pushd $LIB
./odl_reinstaller.sh --cloner-info $CLONER_INFO --odl-artifact $NETVIRT_ARTIFACT
popd