#!/bin/bash

if [[ "$JOB_NAME" =~ (verify|merge|daily|weekly) ]]; then
    JOB_TYPE=${BASH_REMATCH[0]}
else
    echo "Unable to determine job type!"
    exit 1
fi

case "$JOB_TYPE" in
    verify)
        echo "Uploading artifacts for the change $GERRIT_CHANGE_NUMBER. This could take some time..."
        GS_UPLOAD_LOCATION="gs://artifacts.opnfv.org/$PROJECT/review/$GERRIT_CHANGE_NUMBER"
        echo "Removing artifacts produced for the previous patch for the change $GERRIT_CHANGE_NUMBER"
        gsutil rm -r $GS_UPLOAD_LOCATION
        ;;
    daily)
        echo "Uploding daily artifacts This could take some time..."
        OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
        GS_UPLOAD_LOCATION="gs://$GS_URL/$OPNFV_ARTIFACT_VERSION"
        ;;
    *)
        echo "Artifact upload is not enabled for $JOB_TYPE jobs"
        exit 1
esac

gsutil cp -r $WORKSPACE/build_output/* $GS_UPLOAD_LOCATION > $WORKSPACE/gsutil.log 2>&1
gsutil -m setmeta -r \
    -h "Cache-Control:private, max-age=0, no-transform" \
    $GS_UPLOAD_LOCATION > /dev/null 2>&1

gsutil ls $GS_UPLOAD_LOCATION > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Problem while uploading artifacts!"
    echo "Check log $WORKSPACE/gsutil.log on $NODE_NAME"
    exit 1
fi
echo "Uploaded artifacts!"
