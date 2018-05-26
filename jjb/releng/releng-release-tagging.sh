#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 The Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -e -o pipefail

GIT_URL=${GIT_URL:-https://gerrit.opnfv.org/gerrit}
STREAM=${STREAM:-'nostream'}
RELEASE_FILES=$(git diff HEAD^1 --name-only -- "releases/$STREAM")

echo "--> Verifying $RELEASE_FILES."
for release_file in $RELEASE_FILES; do
    # Verify the release file schema
    python releases/scripts/verify_schema.py \
    -s releases/schema.yaml \
    -y $release_file

    # Verify tag for each repo exist and are attached to commits on stable-branch
    while read -r repo tag ref
    do
      echo "--> Cloning $repo"
      if [ ! -d $repo ]; then
          git clone $GIT_URL/$repo.git $repo
      fi
      pushd $repo &> /dev/null

      echo "--> Checking for tag: $tag"
      if ! (git tag -l | grep $tag &> /dev/null); then
          echo "$tag does not exist"
          TAG_EXISTS=false
      else
          git cat-file tag $tag
          TAG_EXISTS=true
      fi

      echo "--> Checking if $ref is on stable/$STREAM"
      if ! (git branch -a --contains $ref | grep "stable/$STREAM"); then
          echo "--> ERROR: $ref for $repo is not on stable/$STREAM!"
          # If the tag exists but is on the wrong ref, there's nothing
          # we can do. But if the tag neither exists nor is on the
          # correct branch we need to fail the verification.
          if [ $TAG_EXISTS = false ]; then
              exit 1
          fi
      else
          if [[ $TAG_EXISTS = false && "$JOB_NAME" =~ "merge" ]]; then
              # If the tag doesn't exist and we're in a merge job,
              # everything has been verified up to this point and we
              # are ready to create the tag.
              git config --global user.name "jenkins-ci"
              git config --global user.email "jenkins-opnfv-ci@opnfv.org"
              echo "--> Creating $tag tag for $repo at $ref"
              git tag -am "$tag" $tag $ref
              echo "--> Pushing tag"
              echo "[noop] git push origin $tag"
          else
              # For non-merge jobs just output the ref info.
              git show -s --format="%h %s %d" $ref
          fi
      fi

      popd &> /dev/null
      echo "--> Done verifing $repo"
    done < <(python releases/scripts/repos.py -f $release_file)
done
