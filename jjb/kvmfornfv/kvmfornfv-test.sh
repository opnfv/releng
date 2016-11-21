#!/bin/bash
##########################################################
##This script includes executing cyclictest scripts.
##########################################################
#The latest build packages are stored in build_output

ls -al $WORKSPACE/build_output

if [[ "$JOB_NAME" =~ (verify|merge|daily|weekly) ]]; then
    JOB_TYPE=${BASH_REMATCH[0]}
else
    echo "Unable to determine job type!"
    exit 1
fi

echo $TEST_NAME

# do stuff differently based on the job type
case "$JOB_TYPE" in
    verify)
        #start the test
        cd $WORKSPACE
        ./ci/test_kvmfornfv.sh $JOB_TYPE
        ;;
    daily)
        #start the test
        cd $WORKSPACE
        ./ci/test_kvmfornfv.sh $JOB_TYPE $TEST_NAME
        ;;
    *)
        echo "Test is not enabled for $JOB_TYPE jobs"
        exit 1
esac
