#!/bin/bash

set -e

# Directory for results
mkdir $WORKSPACE/results/

# Run MongoDB backup
python $WORKSPACE/utils/test/testapi/update/templates/backup_mongodb.py -o $WORKSPACE/results/

# Taring the result file
RESULT_FILE=$WORKSPACE/results/`ls $WORKSPACE/results/`
tar cf $RESULT_FILE\.tar $RESULT_FILE

artifact_dir="testapibackup"

set +e
/usr/local/bin/gsutil &>/dev/null
if [ $? != 0 ]; then
    echo "Not possible to push results to artifact: gsutil not installed"
    exit 1
else
    echo "Uploading mongodump to artifact $artifact_dir"
    /usr/local/bin/gsutil cp -r $RESULT_FILE\.tar gs://artifacts.opnfv.org/"$artifact_dir"/
    echo "MongoDump can be found at http://artifacts.opnfv.org/$artifact_dir"
fi
