#!/bin/bash
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
        GS_LOG_LOCATION="gs://$GS_URL/logs-$(date -u +"%Y-%m-%d")"/
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
source $WORKSPACE/opnfv.properties

# upload artifacts
if [[ "$PHASE" == "build" ]]; then
    gsutil cp -r $WORKSPACE/build_output/* $GS_UPLOAD_LOCATION > $WORKSPACE/gsutil.log 2>&1
    gsutil -m setmeta -r \
        -h "Cache-Control:private, max-age=0, no-transform" \
        $GS_UPLOAD_LOCATION > /dev/null 2>&1
else
    if [[ "$JOB_TYPE" == "daily" ]]; then
        log_dir=$WORKSPACE/build_output/log
        if [[ -d "$log_dir" ]]; then
            #Uploading logs to artifacts
            echo "Uploading artifacts for future debugging needs...."
            gsutil cp -r $WORKSPACE/build_output/log-*.tar.gz $GS_LOG_LOCATION > $WORKSPACE/gsutil.log 2>&1
            # verifying the logs uploaded by cyclictest daily test job
            gsutil ls $GS_LOG_LOCATION > /dev/null 2>&1
            if [[ $? -ne 0 ]]; then
                echo "Problem while uploading logs to artifacts!"
                echo "Check log $WORKSPACE/gsutil.log on $NODE_NAME"
                exit 1
            fi
        else
            echo "No test logs/artifacts available for uploading"
        fi
    fi
fi

# upload metadata file for the artifacts built by daily job
if [[ "$JOB_TYPE" == "daily" && "$PHASE" == "build" ]]; then
    gsutil cp $WORKSPACE/opnfv.properties $GS_UPLOAD_LOCATION/opnfv.properties > $WORKSPACE/gsutil.log 2>&1
    gsutil cp $WORKSPACE/opnfv.properties gs://$GS_URL/latest.properties > $WORKSPACE/gsutil.log 2>&1
    gsutil -m setmeta -r \
        -h "Cache-Control:private, max-age=0, no-transform" \
        $GS_UPLOAD_LOCATION/opnfv.properties \
        gs://$GS_URL/latest.properties > /dev/null 2>&1
fi

# verifying the artifacts uploading by verify/daily build job
if [[ "$PHASE" == "build" ]]; then
    gsutil ls $GS_UPLOAD_LOCATION > /dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        echo "Problem while uploading artifacts!"
        echo "Check log $WORKSPACE/gsutil.log on $NODE_NAME"
        exit 1
    fi
fi
echo "Uploaded artifacts!"
