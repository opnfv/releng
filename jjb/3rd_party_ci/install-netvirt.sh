#!/bin/bash
set -e
. ./odl-pipeline-common.sh
pushd $LIB
  ./odl_reinstaller.sh --cloner-info $CLONER_INFO --odl-artifact $NETVIRT_ARTIFACT
popd