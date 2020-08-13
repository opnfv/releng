#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2020 Samsung Electronics
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

set -o nounset
set -o pipefail
set -o xtrace

if ! command -v shellcheck; then
    # shellcheck disable=SC1091
    source /etc/os-release || source /usr/lib/os-release
    case ${ID,,} in
        *suse*)
            sudo zypper install --gpg-auto-import-keys refresh
            sudo -H -E zypper install -y --no-recommends ShellCheck
        ;;
        ubuntu|debian)
            sudo apt-get update
            sudo -H -E apt-get -y --no-install-recommends install shellcheck
        ;;
        rhel|centos|fedora)
            PKG_MANAGER=$(command -v dnf || command -v yum)
            if ! sudo "$PKG_MANAGER" repolist | grep "epel/"; then
                sudo -H -E "$PKG_MANAGER" -q -y install epel-release
            fi
            sudo "$PKG_MANAGER" updateinfo --assumeyes
            sudo -H -E "${PKG_MANAGER}" -y install ShellCheck
        ;;
    esac
fi

if ! command -v pip; then
    curl -sL https://bootstrap.pypa.io/get-pip.py | sudo python
fi

tox -e lint
bash -c 'shopt -s globstar; shellcheck  **/*.sh'
