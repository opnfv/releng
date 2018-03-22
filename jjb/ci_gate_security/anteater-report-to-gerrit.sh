#!/bin/bash
# SPDX-license-identifier: Apache-2.0
set -o pipefail
EXITSTATUS=0

# This Log should always exist
if [[ -e securityaudit.log ]] ; then

    #check if log has errors
    if grep ERROR securityaudit.log; then
        EXITSTATUS=1
    fi

    grep 'ERROR' securityaudit.log | awk -F"ERROR - " '{ print $2 }' | tr -d "\'\"" > shortlog

    # Only report to Gerrit when there are errors to report.
    if [[ -s shortlog ]]; then
        echo -e "\nposting security audit report to gerrit...\n"
        ssh -p 29418 gerrit.opnfv.org \
            "gerrit review -p $GERRIT_PROJECT \
            -m \"$(cat shortlog)\" \
            $GERRIT_PATCHSET_REVISION \
            --notify NONE"
    fi

    exit $EXITSTATUS
fi
