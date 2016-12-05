#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

SNAP_CACHE=$HOME/snap_cache
# clone opnfv sdnvpn repo
git clone https://gerrit.opnfv.org/gerrit/p/sdnvpn.git $WORKSPACE/sdnvpn

if [ ! -f "$NETVIRT_ARTIFACT" ]; then
  echo "ERROR: ${NETVIRT_ARTIFACT} specified as NetVirt Artifact, but file does not exist"
  exit 1
fi

# TODO (trozet) snapshot should have already been unpacked into cache folder
# but we really should check the cache here, and not use a single cache folder
# for when we support multiple jobs on a single slave
pushd sdnvpn/odl-pipeline/lib > /dev/null
./tripleo_manager.sh --update-opendaylight --pod-config ${SNAP_CACHE}/node.yaml \
  --artifact ${NETVIRT_ARTIFACT} --ssh-key-file ${SNAP_CACHE}/id_rsa
popd > /dev/null
