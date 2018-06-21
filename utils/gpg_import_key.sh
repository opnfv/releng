#!/bin/bash -e
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 NEC and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
function isinstalled {

source /etc/os-release; echo ${ID/*, /}

if [[ ${ID/*, /} =~ "centos" ]]; then
  if rpm -q "$@" >/dev/null 2>&1; then
    true
      else
        echo installing "$1"
        sudo yum install "$1"
    false
  fi

elif [[ ${ID/*, /} =~ "ubuntu" ]]; then
  if dpkg-query -W -f'${Status}' "$@" 2>/dev/null | grep -q "ok installed"; then
    true
      else
        echo installing "$1"
        sudo apt-get install -y "$1"
    false
  fi
else
  echo "Distro not supported"
  exit 0
fi

}

if ! isinstalled gnupg2; then
  echo "error with install"
  exit 0
fi

if ! which gsutil;
  then echo "error gsutil not installed";
  exit 0
fi

if gpg2 --list-keys | grep "opnfv-helpdesk@rt.linuxfoundation.org"; then
  echo "Key Already available"
else
  if [ -z "$NODE_NAME" ];
    then echo "Cannot find node name"
      exit 0
  elif gsutil ls gs://opnfv-signing-keys | grep $NODE_NAME; then
    echo "Importing key for '$NODE_NAME'"
    gsutil cp gs://opnfv-signing-keys/"$NODE_NAME"-subkey .
    gpg2 --import "$NODE_NAME"-subkey
    rm -f "$NODE_NAME"-subkey
  else
    echo "No keys found locally or remotely for host, skipping import"
    exit 0
  fi
fi

