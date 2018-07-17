#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

echo "Detecting requested OpenStack branch and topology type in gerrit comment"
parsed_comment=$(echo $GERRIT_EVENT_COMMENT_TEXT | sed -n 's/^.*check-opnfv\s*//p')
parsed_comment=$(echo $parsed_comment | sed -n 's/\s*$//p')
if [ ! -z "$parsed_comment" ]; then
  if echo $parsed_comment | grep -E '^[a-z]+-(no)?ha'; then
    IFS='-' read -r -a array <<< "$parsed_comment"
    os_version=${array[0]}
    topo=${array[1]}
    echo "OS version detected in gerrit comment: ${os_version}"
    echo "Topology type detected in gerrit comment: ${topo}"
  else
    echo "Invalid format given for scenario in gerrit comment: ${parsed_comment}...aborting"
    exit 1
  fi
else
  echo "No scenario given in gerrit comment, will use default (master OpenStack, noha)"
  os_version='master'
  topo='noha'
fi

echo "Writing variables to file"
cat > detected_snapshot << EOI
OS_VERSION=$os_version
TOPOLOGY=$topo
SNAP_CACHE=$HOME/snap_cache/$os_version/$topo
EOI
