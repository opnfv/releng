#!/bin/bash

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

    gpg2 -vvv --batch --yes --no-tty \
        --default-key opnfv-helpdesk@rt.linuxfoundation.org  \
        --passphrase besteffort \
        --detach-sig $image
    gsutil cp $image.sig gs://$GS_URL/upstream/$image.sig
    echo "Image signature upload complete!"

    # TODO: Kill this if $image.sig can be used instead.
    md5sum -b $image > $image.md5
    gsutil cp $image.md5 gs://$GS_URL/upstream/$image.md5

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
./ci/kolla-build.sh -j $JOB_NAME -w $WORKSPACE/docker_build_dir

image=$(ls $WORKSPACE/docker_build_dir/kolla-build-output/kolla-image-*.tgz)
upload_image_to_opnfv $image

echo
echo "--------------------------------------------------------"
echo "Done!"
