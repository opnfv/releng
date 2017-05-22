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
sudo chmod og+rw ${STORE_FILE_NAME}

OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
GS_UPLOAD_LOCATION="${STORE_URL}/${OPNFV_ARTIFACT_VERSION}"
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
    echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
    echo "OPNFV_ARTIFACT_URL=$GS_UPLOAD_LOCATION"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
) > $WORKSPACE/opnfv.properties
source $WORKSPACE/opnfv.properties

importkey () {
# clone releng repository
echo "Cloning releng repository..."
[ -d releng ] && rm -rf releng
git clone https://gerrit.opnfv.org/gerrit/releng $WORKSPACE/releng/ &> /dev/null
#this is where we import the siging key
if [ -f $WORKSPACE/releng/utils/gpg_import_key.sh ]; then
  source $WORKSPACE/releng/utils/gpg_import_key.sh
fi
}

sign () {
gpg2 -vvv --batch --yes --no-tty \
  --default-key opnfv-helpdesk@rt.linuxfoundation.org  \
  --passphrase besteffort \
  --detach-sig ${CACHE_DIR}/${STORE_FILE_NAME}

gsutil cp ${CACHE_DIR}/${STORE_FILE_NAME}.sig ${STORE_URL}/${STORE_FILE_NAME}.sig
echo "signature Upload Complete!"
}

upload () {
# log info to console
echo "Uploading ${STORE_FILE_NAME} to artifact. This could take some time..."
echo

cd $WORKSPACE
# upload artifact and additional files to google storage
gsutil cp ${CACHE_DIR}/${STORE_FILE_NAME} \
${STORE_URL}/${STORE_FILE_NAME} > gsutil.dockerfile.log 2>&1
gsutil cp $WORKSPACE/opnfv.properties \
${STORE_URL}/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log 2>&1
gsutil cp $WORKSPACE/opnfv.properties \
    ${STORE_URL}/latest.properties > gsutil.latest.log 2>&1

gsutil -m setmeta \
    -h "Content-Type:text/html" \
    -h "Cache-Control:private, max-age=0, no-transform" \
    ${STORE_URL}/latest.properties \
    ${STORE_URL}/opnfv-$OPNFV_ARTIFACT_VERSION.properties > /dev/null 2>&1

gsutil -m setmeta \
    -h "Cache-Control:private, max-age=0, no-transform" \
    ${STORE_URL}/${STORE_FILE_NAME} > /dev/null 2>&1

# disabled errexit due to gsutil setmeta complaints
#   BadRequestException: 400 Invalid argument
# check if we uploaded the file successfully to see if things are fine
gsutil ls ${STORE_URL}/${STORE_FILE_NAME} > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Problem while uploading artifact!"
    exit 1
fi

echo "dovetail: uploading Done!"
echo
echo "--------------------------------------------------------"
echo
}

#importkey
#sign
upload
