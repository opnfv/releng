#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

cd $WORKSPACE/..
sudo rm $WORKSPACE -rf
git clone $GIT_BASE  $WORKSPACE