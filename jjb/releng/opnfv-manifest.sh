#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


set -o errexit
set -o nounset
set -o pipefail

# Starting creating manifest image for $DOCKER_REPO_NAME

ARCH=(amd64 arm64)
DOCKER_REPO_NAME=${DOCKER_REPO_NAME-}
RELEASE_VERSION=${RELEASE_VERSION-}
BRANCH=${BRANCH-}
ARCH_TAG=${ARCH_TAG-}

if [[ "$BRANCH" == "master" ]] || [[ "$BRANCH" == "euphrates" ]]; then
	DOCKER_TAG="latest"
elif [[ -n "${RELEASE_VERSION}" ]]; then
	DOCKER_TAG="${RELEASE_VERSION}"
else
	DOCKER_TAG="stable"
fi
if [[ "${ARCH_TAG}" =~ "arm64" || "${ARCH_TAG}" =~ "amd64" ]]; then
       echo  sudo manifest-tool push from-args --platforms linux/amd64,linux/arm64 \
           --template "${DOCKER_REPO_NAME}":"${ARCH[0]}"-"${DOCKER_TAG}" \
           --template "${DOCKER_REPO_NAME}":"${ARCH[1]}"-"${DOCKER_TAG}" \
           --target "${DOCKER_REPO_NAME}":"${DOCKER_TAG}"
fi

