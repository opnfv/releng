#!/bin/bash

if [[ "$JOB_NAME" =~ (verify|merge|daily|weekly) ]]; then
    JOB_TYPE=${BASH_REMATCH[0]}
else
    echo "Unable to determine job type!"
    exit 1
fi

if [[ "$JOB_TYPE" == "verify" ]]; then
    echo "Downloading artifacts for the change $GERRIT_CHANGE_NUMBER. This could take some time..."
    GS_URL="gs://artifacts.opnfv.org/review/$GERRIT_CHANGE_NUMBER"
else
    echo "Artifact download is not enabled for $JOB_TYPE jobs"
    exit 1
fi

/bin/mkdir -p $WORKSPACE/build_output
gsutil cp -r $GS_URL/* $WORKSPACE/build_output > $WORKSPACE/gsutil.log 2>&1

echo "--------------------------------------------------------"
ls -al $WORKSPACE/build_output
echo "--------------------------------------------------------"

echo "Downloaded artifacts!"
