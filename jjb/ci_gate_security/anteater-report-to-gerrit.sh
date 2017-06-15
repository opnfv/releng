#!/bin/bash
set -o errexit
set -o pipefail
export PATH=$PATH:/usr/local/bin/
EXITSTATUS=0

# This Log should always exist
if [[ -e securityaudit.log ]] ; then
    echo -e "\nposting security audit report to gerrit...\n"

    #check if log has errors
    if grep ERROR securityaudit.log; then
        EXITSTATUS=1
    fi
    
    cat securityaudit.log  | awk -F"ERROR - " '{print $2}' > shortlog
    
    ssh -p 29418 gerrit.opnfv.org \
        "gerrit review -p $GERRIT_PROJECT \
        -m \"$(cat shortlog)\" \
        $GERRIT_PATCHSET_REVISION \
        --notify NONE"
    
    exit $EXITSTATUS
fi
