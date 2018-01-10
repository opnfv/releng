#!/bin/bash
set -e

cd compass4nfv

COMPASS_WORK_DIR=$WORKSPACE/../compass-work
mkdir -p $COMPASS_WORK_DIR
ln -s $COMPASS_WORK_DIR work

#TODO: remove workaround after all arm64 patches merged
curl -s http://people.linaro.org/~yibo.cai/compass/compass4nfv-arm64-fixup.sh | sh

# build tarball
COMPASS_ISO_REPO='http://people.linaro.org/~yibo.cai/compass' ./build.sh
