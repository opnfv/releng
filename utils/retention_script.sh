#!/bin/bash

for x in armband ovsnfv fuel apex compass4nfv
do

  echo "Looking at artifacts for project $x"
  while IFS= read -r artifact; do
  
    artifact_date="$(gsutil ls -L $artifact | grep "Creation time:" | awk '{print $4,$5,$6}')"
    age=$(($(date +%s)-$(date -d"$artifact_date" +%s)))
    daysold=$(($age/86400)) 
  
    if [[ "$daysold" -gt "10" ]]; then
      echo "$daysold Days old Deleting: $(basename $artifact)"
    else
      echo "$daysold Days old Retaining: $(basename $artifact)"
    fi
  
  done < <(gsutil ls gs://artifacts.opnfv.org/"$x" |grep -v "/$")
done
