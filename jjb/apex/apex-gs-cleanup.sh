#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Cleaning Google Storage"
echo "-----------------------"
echo

thirty_days_ago=$(date -d "30 days ago" +"%Y%m%d")

for i in $(gsutil ls gs://$GS_URL/*201?*); do
    filedate=$(date -d "$(echo $i | grep -Eo 201[0-9]-?[0-9][0-9]-?[0-9][0-9])" +"%Y%m%d")
    if [ $filedate -lt $thirty_days_ago ]; then
      # gsutil indicates what it is removing so no need for output here
      gsutil rm $i
    fi
done
