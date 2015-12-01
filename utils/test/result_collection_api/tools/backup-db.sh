#!/bin/bash

echo "Backup Test collection DB"
now=$(date +"%m_%d_%Y_%H_%M_%S")
echo $now
echo " ------------- "
TARGET_DIR=./$now
TEST_RESULT_DB_BACKUP="test_collection_db."$now".tar.gz"

echo "Create Directory for backup"
mkdir -p $TARGET_DIR

echo "Export results"
mongoexport -db test_results_collection -c test_results --out $TARGET_DIR/results.json
echo "Export test cases"
mongoexport --db test_results_collection -c test_cases --out $TARGET_DIR/backup-cases.json
echo "Export projects"
mongoexport --db test_results_collection -c test_projects --out $TARGET_DIR/backup-projects.json
echo "Export pods"
mongoexport --db test_results_collection -c pod --out $TARGET_DIR/backup-pod.json

echo "Create tar.gz"
tar -cvzf $TEST_RESULT_DB_BACKUP $TARGET_DIR

echo "Delete temp directory"
rm -Rf $TARGET_DIR
