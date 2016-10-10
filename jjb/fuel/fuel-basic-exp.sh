#!/bin/bash
set -o nounset

echo "-----------------------------------------------------------------------"
echo $GERRIT_CHANGE_COMMIT_MESSAGE
echo "-----------------------------------------------------------------------"

# proposal for specifying the scenario name in commit message
# currently only 1 scenario name is supported but depending on
# the need, it can be expanded, supporting multiple scenarios
# using comma separated list or something
SCENARIO_NAME_PATTERN="(?<=@scenario:).*?(?=@)"
SCENARIO_NAME=(echo $GERRIT_CHANGE_COMMIT_MESSAGE | grep -oP "$SCENARIO_NAME_PATTERN")
if [[ $? -ne 0 ]]; then
    echo "The patch verification will be done only with build!"
else
    echo "Will run full verification; build, deploy, and smoke test using scenario $SCENARIO_NAME"
fi
