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
TAG=${TAG:-"opnfv-0.0.0"}
TAG_EXISTS=false
STREAM=${STREAM:-'nostream'}
RELEASE_FILES=$(git diff HEAD^1 --name-only -- "releases/$STREAM")

echo "--> Verifying $TAG in $RELEASE_FILES."
for release_file in $RELEASE_FILES; do
    # Verify the release file schema
    python releases/scripts/verify_schema.py \
    -s releases/schema.yaml \
    -y $release_file

    # Verify tag for each repo exist and are attached to commits on stable-branch
    while read -r repo ref
    do
      echo "--> Cloning $repo"
      git clone $GIT_URL/$repo.git $repo
      pushd $repo &> /dev/null

      echo "--> Checking for tag: $TAG"
      if ! (git tag -l | grep $TAG &> /dev/null); then
          echo "$TAG does not exist"
      else
          git cat-file tag $TAG
          TAG_EXISTS=true
      fi

      echo "--> Checking if $ref is on stable/$STREAM"
      if ! (git branch -a --contains $ref | grep "stable/$STREAM"); then
          echo "--> ERROR: $ref for $repo is not on stable/$STREAM!"
          # If the tag exists but is on the wrong ref, there's nothing
          # we can do. But if the tag neither exists nor is on the
          # correct branch we need to fail the verification.
          if [ ! $TAG_EXISTS ]; then
              if [[ "$JOB_NAME" =~ "merge" ]]; then
                  # If the tag doesn't exist and we're in a merge job,
                  # everything has been verified up to this point and we
                  # are ready to create the tag.
                  echo "--> Creating $TAG tag for $repo at $ref"
                  git tag -am "$TAG" $TAG $ref
                  echo "--> Pushing tag"
                  echo "[noop] git push origin $TAG"
              else
                  exit 1
              fi
          fi
      else
          git show -s --format="%h %s %d" $ref
      fi

      popd &> /dev/null
      echo "--> Done verifing $repo"
    done < <(python releases/scripts/repos.py -r $TAG -f $release_file)
done
