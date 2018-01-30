#!/bin/bash
set -o nounset
set -o pipefail

# log info to console
echo "Uploading the logs $INSTALLER_TYPE artifact. This could take some time..."
echo "--------------------------------------------------------"
echo

# create the log directory if it doesn't exist
[[ -d $LOG_DIRECTORY ]] || mkdir -p $LOG_DIRECTORY

OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d_%H-%M-%S")
COMPASS_LOG_FILENAME="${JOB_NAME}_${BUILD_NUMBER}_${OPNFV_ARTIFACT_VERSION}.log.tar.gz"


sudo docker exec -it compass-tasks /bin/bash /opt/collect-log.sh
sudo docker cp compass-tasks:/opt/log.tar.gz ${LOG_DIRECTORY}/${COMPASS_LOG_FILENAME}

sudo chown $(whoami):$(whoami) ${LOG_DIRECTORY}/${COMPASS_LOG_FILENAME}

gsutil cp "${LOG_DIRECTORY}/${COMPASS_LOG_FILENAME}" \
     "gs://${GS_URL}/logs/${COMPASS_LOG_FILENAME}" > /dev/null 2>&1

echo
echo "--------------------------------------------------------"
echo "Done!"
echo "Artifact is available as http://${GS_URL}/logs/${COMPASS_LOG_FILENAME}"
