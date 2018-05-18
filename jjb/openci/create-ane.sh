#!/bin/bash

cat << EOF > $WORKSPACE/event.properties
eventType=$EVENT_TYPE
eventOrigin=$EVENT_ORIGIN
eventBody="{ 'type': '$EVENT_TYPE', 'id': '$(uuidgen)', 'time': '$(date -u +%Y-%m-%d_%H:%M:%SUTC)', 'origin': '$EVENT_ORIGIN', 'buildUrl': '$BUILD_URL', 'branch': 'master', 'artifactLocation': 'https://url/to/artifact', 'confidenceLevel': { $CONFIDENCE_LEVEL } }"
EOF
echo "Constructed $EVENT_TYPE"
echo "--------------------------------------------"
cat $WORKSPACE/event.properties
echo "--------------------------------------------"
