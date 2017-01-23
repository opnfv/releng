#!/bin/bash

set -e

# Directory for results
mkdir $WORKSPACE/results/

# Run MongoDB backup
python $WORKSPACE/utils/test/testapi/update/templates/backup_mongodb.py -o $WORKSPACE/results/

workspace=$WORKSPACE
artifact_dir="testing"

set +e
gsutil&>/dev/null
if [ $? != 0 ]; then
    echo "Not possible to push results to artifact: gsutil not installed"
    exit 1
else
    echo "Uploading mongodump to artifact $artifact_dir"
    gsutil cp -r "$workspace"/results/test_results_collection* gs://artifacts.opnfv.org/"$artifact_dir"/
    echo "MongoDump can be found at http://artifacts.opnfv.org/$artifact_dir"
fi
