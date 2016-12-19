#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Huawei Technologies Co.,Ltd and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o pipefail

echo "dovetail: pull and save the images"

[[ -d ${CACHE_DIR} ]] || mkdir -p ${CACHE_DIR}

cd ${CACHE_DIR}
sudo docker pull ${DOCKER_REPO_NAME}:${DOCKER_TAG}
sudo docker save -o ${STORE_FILE_NAME} ${DOCKER_REPO_NAME}:${DOCKER_TAG}

echo "dovetail: upload image to artifacts.opnfv.org, which can be for offline usage"
gsutil cp ${CACHE_DIR}/${STORE_FILE_NAME} ${STORE_URL}

echo "dovetail: uploading done"
