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


set -o errexit
set -o nounset
set -o pipefail

importkey () {
    # clone releng repository
    echo "Cloning releng repository..."
    [ -d releng ] && rm -rf releng
    git clone https://gerrit.opnfv.org/gerrit/releng ./releng/ &> /dev/null
    #this is where we import the siging key
    if [ -f ./releng/utils/gpg_import_key.sh ]; then
        source ./releng/utils/gpg_import_key.sh
    fi
}

upload_image_to_opnfv () {
    image=$1

    importkey
    if gpg2 --list-keys | grep "opnfv-helpdesk@rt.linuxfoundation.org"; then
        echo "Signing Key avaliable"
        SIGN_ARTIFACT="true"
    fi

    if [[ -n "$SIGN_ARTIFACT" && "$SIGN_ARTIFACT" == "true" ]]; then
        gpg2 -vvv --batch --yes --no-tty \
            --default-key opnfv-helpdesk@rt.linuxfoundation.org  \
            --passphrase besteffort \
            --detach-sig $image
        gsutil cp $image.sig gs://$GS_URL/upstream/$image.sig
        echo "Image signature upload complete!"
    fi

    sha512sum -b $image > $image.sha512sum
    gsutil cp $image.sha512sum gs://$GS_URL/upstream/$image.sha512sum

    echo "Uploading $INSTALLER_TYPE artifact. This could take some time..."
    echo
    gsutil cp $image gs://$GS_URL/upstream/$image
    gsutil -m setmeta \
        -h "Cache-Control:private, max-age=0, no-transform" \
        gs://$GS_URL/upstream/$image

    # check if we uploaded the file successfully to see if things are fine
    gsutil ls gs://$GS_URL/upstream/$image
    if [[ $? -ne 0 ]]; then
        echo "Problem while uploading artifact!"
        exit 1
    fi
}



echo "--------------------------------------------------------"
echo "This is diasy4nfv kolla image build job!"
echo "--------------------------------------------------------"

# start the build
cd $WORKSPACE
rm -rf docker_build_dir
mkdir -p docker_build_dir

# -j is for deciding which branch will be used when building,
# only for OPNFV
sudo -E ./ci/kolla-build.sh -j $JOB_NAME -w $WORKSPACE/docker_build_dir

if [ $? -ne 0 ]; then
    echo
    echo "Kolla build failed!"
    deploy_ret=1
else
    echo
    echo "--------------------------------------------------------"
    echo "Kolla build done!"
fi

image=$(ls $WORKSPACE/docker_build_dir/kolla-build-output/kolla-image-*.tgz)
upload_image_to_opnfv $image

echo
echo "--------------------------------------------------------"
echo "All done!"
