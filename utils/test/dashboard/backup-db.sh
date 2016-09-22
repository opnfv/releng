#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Orange and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
echo "Backup Test collection DB"
now=$(date +"%m_%d_%Y_%H_%M_%S")
echo $now
echo " ------------- "
TARGET_DIR=./$now
TEST_RESULT_DB_BACKUP="test_collection_db."$now".tar.gz"

echo "Create Directory for backup"
mkdir -p $TARGET_DIR

echo "Export results"
mongoexport --db test_results_collection -c results --out $TARGET_DIR/backup-results.json
echo "Export test cases"
mongoexport --db test_results_collection -c testcases --out $TARGET_DIR/backup-cases.json
echo "Export projects"
mongoexport --db test_results_collection -c projects --out $TARGET_DIR/backup-projects.json
echo "Export pods"
mongoexport --db test_results_collection -c pods --out $TARGET_DIR/backup-pod.json

echo "Create tar.gz"
#tar -cvzf $TEST_RESULT_DB_BACKUP $TARGET_DIR

echo "Delete temp directory"
#rm -Rf $TARGET_DIR
