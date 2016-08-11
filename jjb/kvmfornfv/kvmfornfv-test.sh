#!/bin/bash
##########################################################
##This script includes executing cyclictest scripts.
##########################################################
#The latest build packages are stored in build_output
ls -al $WORKSPACE/build_output

#start the test
cd $WORKSPACE
./ci/test_kvmfornfv.sh
