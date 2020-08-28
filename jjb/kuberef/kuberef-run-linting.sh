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

# _vercmp() - Function that compares two versions
function _vercmp {
    local v1=$1
    local op=$2
    local v2=$3
    local result

    # sort the two numbers with sort's "-V" argument.  Based on if v2
    # swapped places with v1, we can determine ordering.
    result=$(echo -e "$v1\n$v2" | sort -V | head -1)

    case $op in
        "==")
            [ "$v1" = "$v2" ]
            return
            ;;
        ">")
            [ "$v1" != "$v2" ] && [ "$result" = "$v2" ]
            return
            ;;
        "<")
            [ "$v1" != "$v2" ] && [ "$result" = "$v1" ]
            return
            ;;
        ">=")
            [ "$result" = "$v2" ]
            return
            ;;
        "<=")
            [ "$result" = "$v1" ]
            return
            ;;
        *)
            die $LINENO "unrecognised op: $op"
            ;;
    esac
}

echo "Requirements validation"
# shellcheck disable=SC1091
source /etc/os-release || source /usr/lib/os-release

min_shellcheck_version=0.4.0
min_tox_version=3.5

pkgs=""
if ! command -v shellcheck; then
    case ${ID,,} in
        *suse*|rhel|centos|fedora)
            pkgs="ShellCheck"
        ;;
        ubuntu|debian)
            pkgs="shellcheck"
        ;;
    esac
fi
if ! command -v pip; then
    case ${ID,,} in
        *suse*|rhel|centos|fedora)
            pkgs+=" python3-pip python3-setuptools"
        ;;
        ubuntu|debian)
            if _vercmp "${VERSION_ID}" '<=' "18.04"; then
                pkgs+=" python-pip python-setuptools"
            else
                pkgs+=" python3-pip python3-setuptools"
            fi
        ;;
    esac
fi

if [ -n "$pkgs" ]; then
    echo "Requirements installation"
    case ${ID,,} in
        *suse*)
            sudo zypper install --gpg-auto-import-keys refresh
            eval "sudo -H -E zypper install -y --no-recommends $pkgs"
        ;;
        ubuntu|debian)
            sudo apt-get update
            eval "sudo -H -E apt-get -y --no-install-recommends install $pkgs"
        ;;
        rhel|centos|fedora)
            PKG_MANAGER=$(command -v dnf || command -v yum)
            if ! sudo "$PKG_MANAGER" repolist | grep "epel/"; then
                sudo -H -E "$PKG_MANAGER" -q -y install epel-release
            fi
            sudo "$PKG_MANAGER" updateinfo --assumeyes
            eval "sudo -H -E ${PKG_MANAGER} -y install $pkgs"
        ;;
    esac
    if ! command -v pip && command -v pip3 ; then
        sudo ln -s "$(command -v pip3)" /usr/bin/pip
    fi
    eval "sudo $(command -v pip) install --upgrade pip"
fi

if ! command -v tox || _vercmp "$(tox --version | awk '{print $1}')" '<' "$min_tox_version"; then
    eval "sudo $(command -v pip) install tox==$min_tox_version"
fi

echo "Server tools information:"
python -V
tox --version
shellcheck -V

echo "Linting process execution"
tox -e lint
if _vercmp "$(shellcheck --version | awk 'FNR==2{print $2}')" '<' "$min_shellcheck_version"; then
    bash -c 'shopt -s globstar; shellcheck **/*.sh'
else
    bash -c 'shopt -s globstar; shellcheck -x **/*.sh'
fi
