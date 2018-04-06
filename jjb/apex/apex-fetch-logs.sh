#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Fetching logs from overcloud. This could take some time..."
echo "--------------------------------------------------------"
echo

if sudo opnfv-pyutil --fetch-logs; then
  LOG_LOCATION=$(cat apex_util.log | grep 'Log retrieval complete' | grep -Eo '/tmp/.+$')
  if [ -z "$LOG_LOCATION" ]; then
      echo "WARNING: Unable to determine log location.  Logs will not be uploaded"
      exit 0
  else
    sudo chmod 777 ${LOG_LOCATION}
    UPLOAD_LOCATION="${GS_URL}/logs/${JOB_NAME}/${BUILD_NUMBER}/"
    gsutil -m cp -r ${LOG_LOCATION} gs://${UPLOAD_LOCATION} > gsutil.latest_logs.log
    echo -e "Logs available at: \n$(find ${LOG_LOCATION} -type f | sed -n 's#^/tmp/#http://'$UPLOAD_LOCATION'#p')"
  fi
else
  echo "WARNING: Log retrieval failed.  No logs will be uploaded"
  exit 0
fi
