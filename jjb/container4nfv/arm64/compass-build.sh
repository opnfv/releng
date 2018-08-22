#!/bin/bash
set -e

cd compass4nfv

COMPASS_WORK_DIR=$WORKSPACE/../compass-work
mkdir -p $COMPASS_WORK_DIR
ln -s $COMPASS_WORK_DIR work

sudo docker rm -f `docker ps | grep compass | cut -f1 -d' '` || true

curl -s http://people.linaro.org/~yibo.cai/compass/compass4nfv-arm64-fixup.sh | bash -s {scenario} || true

./build.sh
