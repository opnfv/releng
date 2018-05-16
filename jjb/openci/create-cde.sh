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

# This script creates CompositionDefinedEvent
# The JMS Messaging Plugin doesn't handle the newlines well so the eventBody is
# constructed on a single line. This is something that needs to be fixed properly

cat << EOF > $WORKSPACE/event.properties
type=$PUBLISH_EVENT_TYPE
origin=$PUBLISH_EVENT_ORIGIN
scenario=$DEPLOY_SCENARIO
eventBody="{ 'type': '$EVENT_TYPE', 'id': '$(uuidgen)', 'time': '$(date -u +%Y-%m-%d_%H:%M:%SUTC)', 'origin': '$EVENT_ORIGIN', 'buildUrl': '$BUILD_URL', 'branch': 'master', 'compositionName': '$DEPLOY_SCENARIO', 'compositionMetadataUrl': '$SCENARIO_METADATA' }"
EOF
echo "Constructed $EVENT_TYPE"
echo "--------------------------------------------"
cat $WORKSPACE/event.properties
echo "--------------------------------------------"
