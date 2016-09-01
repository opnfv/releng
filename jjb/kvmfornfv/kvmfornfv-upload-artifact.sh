#!/bin/bash
set -o errexit
set -o nounset

if [[ "$JOB_NAME" =~ (verify|merge|daily|weekly) ]]; then
    JOB_TYPE=${BASH_REMATCH[0]}
else
    echo "Unable to determine job type!"
    exit 1
fi

case "$JOB_TYPE" in
    verify)
        OPNFV_ARTIFACT_VERSION="gerrit-$GERRIT_CHANGE_NUMBER"
        GS_UPLOAD_LOCATION="gs://artifacts.opnfv.org/$PROJECT/review/$GERRIT_CHANGE_NUMBER"
        echo "Removing outdated artifacts produced for the previous patch for the change $GERRIT_CHANGE_NUMBER"
        gsutil ls $GS_UPLOAD_LOCATION > /dev/null 2>&1 && gsutil rm -r $GS_UPLOAD_LOCATION
        echo "Uploading artifacts for the change $GERRIT_CHANGE_NUMBER. This could take some time..."
        ;;
    daily)
        echo "Uploading daily artifacts This could take some time..."
        OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
        GS_UPLOAD_LOCATION="gs://$GS_URL/$OPNFV_ARTIFACT_VERSION"
        ;;
    *)
        echo "Artifact upload is not enabled for $JOB_TYPE jobs"
        exit 1
esac

# save information regarding artifacts into file
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
    echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
    echo "OPNFV_ARTIFACT_URL=$GS_UPLOAD_LOCATION"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
) > $WORKSPACE/opnfv.properties

# upload artifacts
gsutil cp -r $WORKSPACE/build_output/* $GS_UPLOAD_LOCATION > $WORKSPACE/gsutil.log 2>&1
gsutil -m setmeta -r \
    -h "Cache-Control:private, max-age=0, no-transform" \
    $GS_UPLOAD_LOCATION > /dev/null 2>&1

# upload metadata file for the artifacts built by daily job
if [[ "$JOB_TYPE" == "daily" ]]; then
    gsutil cp -r $WORKSPACE/opnfv.properties $GS_UPLOAD_LOCATION/opnfv-${OPNFV_ARTIFACT_VERSION}.properties > $WORKSPACE/gsutil.log 2>&1
    gsutil cp -r $WORKSPACE/opnfv.properties $GS_URL/latest.properties > $WORKSPACE/gsutil.log 2>&1
    gsutil -m setmeta -r \
        -h "Cache-Control:private, max-age=0, no-transform" \
        $GS_UPLOAD_LOCATION/opnfv-${OPNFV_ARTIFACT_VERSION}.properties \
        $GS_URL/latest.properties > /dev/null 2>&1
fi

gsutil ls $GS_UPLOAD_LOCATION > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Problem while uploading artifacts!"
    echo "Check log $WORKSPACE/gsutil.log on $NODE_NAME"
    exit 1
fi
echo "Uploaded artifacts!"
