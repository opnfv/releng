#!/bin/bash
set -e

cd compass4nfv

COMPASS_WORK_DIR=$WORKSPACE/../compass-work
mkdir -p $COMPASS_WORK_DIR
ln -s $COMPASS_WORK_DIR work

#TODO: remove workaround after compass4nfv patches merged
git checkout 522bce77aee6680a977fa7d0acac3d4091202377
curl http://people.linaro.org/~yibo.cai/compass/0001-deploy-cobbler-drop-tcp_tw_recycle-in-sysctl.conf.patch | git apply
curl http://people.linaro.org/~yibo.cai/compass/0002-docker-compose-support-aarch64.patch | git apply
curl http://people.linaro.org/~yibo.cai/compass/0003-add-a-multus-with-2-fannel-interfaces-installation.patch | git apply
curl http://people.linaro.org/~yibo.cai/compass/0004-deploy-remove-gic-version-in-arm-vm-template.patch | git apply

# build tarball
COMPASS_ISO_REPO='http://people.linaro.org/~yibo.cai/compass' ./build.sh
