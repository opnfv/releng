#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# Expects a file: repos.txt to exists before this script is ran
# containing a list of repos and refs in the form of:
#
# reponame 01234567890123456789
#

# TODO: Handle the case where a repository already has a tag
# TODO: TMPDIR can probably exist in WORKSPACE

TAG=opnfv-6.0.0
TAG_BRANCH=stable/fraser
TMPDIR=/var/tmp/opnfv-release

function cleanup() {
  cd $TMPDIR || exit
  rm -r $name
}

mkdir -p $TMPDIR

while read -r name ref
do
  if [ ! -d "$TMPDIR/$name" ]; then
      echo "--> Cloning $name to $TMPDIR/$name"
      git clone ssh://$USER@gerrit.opnfv.org:29418/$name.git $TMPDIR/$name
  fi
  echo "--> Changing directory to $TMPDIR/$name"
  pushd $TMPDIR/$name &> /dev/null
  echo "--> Verifing $ref is on $TAG_BRANCH"
  if ! git branch -a --contains $ref | grep $TAG_BRANCH; then
      echo "--> Aborting: $ref is not on $TAG_BRANCH branch!"
      cleanup
      exit 1
  fi
  echo "--> Creating $TAG tag for $name at $ref"
  git tag -am "$TAG" $TAG $ref
  echo "--> Push tag"
  echo "[noop] git push origin $TAG"
  cleanup
  popd &> /dev/null
done < repos.txt
