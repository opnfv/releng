#!/bin/bash
set -x
set -o errexit
set -o nounset
set -o pipefail
# make ppa
cd $WORKSPACE/
./build/make_repo.sh
# calc MD5 of ppa
cd $PPA_CACHE
for i in $(find *.gz *.iso *.img -type f)
do
    md5=$(md5sum $i | cut -d ' ' -f1)
    echo $md5 > $i.md5
    curl -T $i $PPA_REPO
    curl -T $i.md5 $PPA_REPO
done