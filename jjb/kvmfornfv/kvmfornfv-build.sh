#!/bin/bash

# build output directory
OUTPUT_DIR=$WORKSPACE/build_output
mkdir -p $OUTPUT_DIR

# start the build
cd $WORKSPACE
./ci/build.sh $OUTPUT_DIR
