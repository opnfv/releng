#!/bin/bash

set -e

# Run MongoDB backup
python $WORKSPACE/utils/test/testapi/update/templates/backup_mongodb.py -o $WORKSPACE/

# Compressing the dump
now=$(date +"%m_%d_%Y_%H_%M_%S")
echo $now

file_name="testapi_mongodb_"$now".tar.gz"
echo $file_name

tar cvfz "$file_name" test_results_collection*

rm -rf test_results_collection*

artifact_dir="testapibackup"
workspace="$WORKSPACE"

set +e
/usr/local/bin/gsutil &>/dev/null
if [ $? != 0 ]; then
    echo "Not possible to push results to artifact: gsutil not installed"
    exit 1
else
    echo "Uploading mongodump to artifact $artifact_dir"
    /usr/local/bin/gsutil cp -r "$workspace"/"$file_name" gs://testingrohit/"$artifact_dir"/
    echo "MongoDump can be found at http://artifacts.opnfv.org/$artifact_dir"
fi
