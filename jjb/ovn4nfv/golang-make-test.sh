#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 Intel Corporation.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o pipefail

source /etc/os-release || source /usr/lib/os-release
case ${ID,,} in
    ubuntu|debian)
    sudo apt-get install mercurial
    sudo add-apt-repository -y ppa:longsleep/golang-backports
    sudo apt-get update
    sudo apt-get install -y build-essential golang-go
    sudo apt-get -y clean && sudo apt-get -y autoremove
    ;;
esac

echo "Running unit tests in Go ${golang_version} ..."
cd $WORKSPACE
make test
