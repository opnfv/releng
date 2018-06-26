#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

SNAP_CACHE=$HOME/snap_cache
# clone opnfv sdnvpn repo
git clone https://gerrit.opnfv.org/gerrit/p/sdnvpn.git $WORKSPACE/sdnvpn

if [ ! -f "/tmp/${NETVIRT_ARTIFACT}" ]; then
  echo "ERROR: /tmp/${NETVIRT_ARTIFACT} specified as NetVirt Artifact, but file does not exist"
  exit 1
fi

if [ ! -f "${SNAP_CACHE}/node.yaml" ]; then
  echo "ERROR: node.yaml pod config missing in ${SNAP_CACHE}"
  exit 1
fi

if [ ! -f "${SNAP_CACHE}/id_rsa" ]; then
  echo "ERROR: id_rsa ssh creds missing in ${SNAP_CACHE}"
  exit 1
fi

# TODO (trozet) snapshot should have already been unpacked into cache folder
# but we really should check the cache here, and not use a single cache folder
# for when we support multiple jobs on a single slave
pushd sdnvpn/odl-pipeline/lib > /dev/null
git fetch https://gerrit.opnfv.org/gerrit/sdnvpn refs/changes/17/59017/5 && git checkout FETCH_HEAD
./odl_reinstaller.sh --pod-config ${SNAP_CACHE}/node.yaml \
  --odl-artifact /tmp/${NETVIRT_ARTIFACT} --ssh-key-file ${SNAP_CACHE}/id_rsa
popd > /dev/null
