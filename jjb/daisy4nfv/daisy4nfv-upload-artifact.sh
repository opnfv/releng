#!/bin/bash
##############################################################################
# Copyright (c) 2016 ZTE Coreporation and others.
# hu.zhijiang@zte.com.cn
# sun.jing22@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o pipefail

# check if we built something
if [ -f $WORKSPACE/.noupload ]; then
    echo "Nothing new to upload. Exiting."
    /bin/rm -f $WORKSPACE/.noupload
    exit 0
fi

# source the opnfv.properties to get ARTIFACT_VERSION
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

signbin () {
gpg2 -vvv --batch --yes --no-tty \
  --default-key opnfv-helpdesk@rt.linuxfoundation.org  \
  --passphrase besteffort \
  --detach-sig $BUILD_DIRECTORY/opnfv-$OPNFV_ARTIFACT_VERSION.bin

gsutil cp $BUILD_DIRECTORY/opnfv-$OPNFV_ARTIFACT_VERSION.bin.sig gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.bin.sig
echo "BIN signature Upload Complete!"
}

uploadbin () {
# log info to console
echo "Uploading $INSTALLER_TYPE artifact. This could take some time..."
echo

cd $WORKSPACE
# upload artifact and additional files to google storage
gsutil cp $BUILD_DIRECTORY/opnfv-$OPNFV_ARTIFACT_VERSION.bin \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.bin > gsutil.bin.log 2>&1
gsutil cp $BUILD_DIRECTORY/opnfv-$OPNFV_ARTIFACT_VERSION.iso \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.bin >> gsutil.bin.log 2>&1
gsutil cp $WORKSPACE/opnfv.properties \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > gsutil.properties.log 2>&1
if [[ ! "$JOB_NAME" =~ (verify|merge) ]]; then
    gsutil cp $WORKSPACE/opnfv.properties \
    gs://$GS_URL/latest.properties > gsutil.latest.log 2>&1
elif [[ "$JOB_NAME" =~ "merge" ]]; then
    echo "Uploaded Daisy4nfv artifacts for a merged change"
fi

gsutil -m setmeta \
    -h "Content-Type:text/html" \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/latest.properties \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.properties > /dev/null 2>&1

gsutil -m setmeta \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.bin > /dev/null 2>&1

# disabled errexit due to gsutil setmeta complaints
#   BadRequestException: 400 Invalid argument
# check if we uploaded the file successfully to see if things are fine
gsutil ls gs://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.bin > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Problem while uploading artifact!"
    echo "Check log $WORKSPACE/gsutil.bin.log on the machine where this build is done."
    exit 1
fi

echo "Done!"
echo
echo "--------------------------------------------------------"
echo
echo "Artifact is available as http://$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.bin"
echo
echo "--------------------------------------------------------"
echo
}

importkey
signbin
uploadbin
