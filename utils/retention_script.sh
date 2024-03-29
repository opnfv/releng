#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 The Linux Foundation and others
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

for x in airship apex armband compass4nfv fuel ovsnfv
do

  echo "Looking at artifacts for project $x"
  echo "In path gs://artifacts.opnfv.org/$x"

  while IFS= read -r artifact; do

    artifact_date="$(gsutil ls -L $artifact | grep "Creation time:" | awk '{print $4,$5,$6}')"
    age=$(($(date +%s)-$(date -d"$artifact_date" +%s)))
    daysold=$(($age/86400))

    if [[ "$daysold" -gt "10" ]]; then
      echo "$daysold Days old deleting: $(basename $artifact)"
      gsutil rm "$artifact"
    else
      echo "$daysold Days old retaining: $(basename $artifact)"
    fi

  done < <(gsutil ls gs://artifacts.opnfv.org/"$x" |grep -v "/$")
done
