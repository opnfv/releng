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
if rpm -qa "$@" >/dev/null 2>&1; then
  true
    else
      echo installing "$1"
      sudo yum install "$1"
  false
fi
}

if ! isinstalled gnupg2; then
  echo "error with install"
  exit 1
fi

if ! which gsutil;
  then echo "error gsutil not installed";
  exit 1
fi

if gpg2 --list-keys | grep "opnfv-helpdesk@rt.linuxfoundation.org"; then
  echo "Key Already available"
else
  if [ -z "$NODE_NAME" ];
    then echo "Cannot find node name"
      exit 1
    else echo "Importing key for '$NODE_NAME'";
     gsutil cp gs://opnfv-signing-keys/"$NODE_NAME"-subkey .
     gpg2 --import "$NODE_NAME"-subkey
     rm -f "$NODE_NAME"-subkey
   fi
fi
