#!/bin/bash

if [[ "$JOB_NAME" =~ (verify|merge|daily|weekly) ]]; then
    JOB_TYPE=${BASH_REMATCH[0]}
else
    echo "Unable to determine job type!"
    exit 1
fi

if [[ "$JOB_TYPE" == "verify" ]]; then
    echo "Uploding artifacts for the change $GERRIT_CHANGE_NUMBER. This could take some time..."
    GS_URL="gs://artifacts.opnfv.org/review/$GERRIT_CHANGE_NUMBER"
else
    echo "Artifact upload is not enabled for $JOB_TYPE jobs"
    exit 1
fi

gsutil cp -r $WORKSPACE/build_output $GS_URL > $WORKSPACE/gsutil.log 2>&1
gsutil -m setmeta -r \
    -h "Cache-Control:private, max-age=0, no-transform" \
    $GS_URL > /dev/null 2>&1

gsutil ls $GS_URL > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Problem while uploading artifacts!"
    echo "Check log $WORKSPACE/gsutil.log on $NODE_NAME"
    exit 1
fi
echo "Uploaded artifacts!"
