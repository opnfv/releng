#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2018 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

export PS1=${PS1:-}

# This script creates ConfidenceLevelModifiedEvent

git clone https://gitlab.openci.io/openci/prototypes.git
cd prototypes/federated-cicd
virtualenv openci_publish
cd openci_publish
source bin/activate
python setup.py install

# generate event body
cat <<EOF > ./json_body.txt
{
    "type": "$PUBLISH_EVENT_TYPE",
    "id": "$(uuidgen)",
    "time": "$(date -u +%Y-%m-%d_%H:%M:%SUTC)",
    "buildUrl": "$BUILD_URL",
    "branch": "master",
    "origin": "$PUBLISH_EVENT_ORIGIN",
    "scenario": "$DEPLOY_SCENARIO",
    "compositionName": "$DEPLOY_SCENARIO",
    "compositionMetadataUrl": "$SCENARIO_METADATA_LOCATION",
    "confidenceLevel": "$CONFIDENCE_LEVEL"
}
EOF

echo "Constructed $PUBLISH_EVENT_TYPE"
echo "--------------------------------------------"
cat ./json_body.txt
echo "--------------------------------------------"

python openci_publish -H 129.192.69.55 -U ${ACTIVEMQ_USER} -p ${ACTIVEMQ_PASSWORD} -n openci.prototype -B ./json_body.txt

deactivate
