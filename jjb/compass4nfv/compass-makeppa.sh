#!/bin/bash
set -x
set -o errexit
set -o nounset
set -o pipefail
# make ppa
cd $WORKSPACE/
./build/make_repo.sh
# calc SHA512 of ppa
cd $PPA_CACHE
for i in $(find *.gz *.iso *.img -type f)
do
    sha512sum=$(sha512sum $i | cut -d ' ' -f1)
    echo $sha512sum > $i.sha512
    curl -T $i $PPA_REPO
    curl -T $i.sha512 $PPA_REPO
done
