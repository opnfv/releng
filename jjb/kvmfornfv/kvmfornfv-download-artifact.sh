#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

if [[ "$JOB_NAME" =~ (verify|merge|daily|weekly) ]]; then
    JOB_TYPE=${BASH_REMATCH[0]}
else
    echo "Unable to determine job type!"
    exit 1
fi

# do stuff differently based on the job type
case "$JOB_TYPE" in
    verify)
        echo "Downloading artifacts for the change $GERRIT_CHANGE_NUMBER. This could take some time..."
        GS_UPLOAD_LOCATION="gs://artifacts.opnfv.org/$PROJECT/review/$GERRIT_CHANGE_NUMBER"
        ;;
    daily)
        gsutil cp gs://$GS_URL/latest.properties $WORKSPACE/latest.properties
        source $WORKSPACE/latest.properties
        GS_UPLOAD_LOCATION=$OPNFV_ARTIFACT_URL
        echo "Downloading artifacts from $GS_UPLOAD_LOCATION for daily run. This could take some time..."
        ;;
    *)
        echo "Artifact download is not enabled for $JOB_TYPE jobs"
        exit 1
esac

/bin/mkdir -p $WORKSPACE/build_output
gsutil cp -r $GS_UPLOAD_LOCATION/* $WORKSPACE/build_output > $WORKSPACE/gsutil.log 2>&1

echo "--------------------------------------------------------"
ls -al $WORKSPACE/build_output
echo "--------------------------------------------------------"
echo
echo "Downloaded artifacts!"
