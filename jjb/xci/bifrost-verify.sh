#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

trap cleanup_and_upload EXIT

function upload_logs() {
    BIFROST_CONSOLE_LOG="${BUILD_URL}/consoleText"
    BIFROST_GS_URL=${BIFROST_LOG_URL/http:/gs:}

    # Make sure the old landing page is gone in case
    # we break later on. We don't want to publish
    # stale information.
    # TODO: Maybe cleanup the entire $BIFROST_GS_URL directory
    # before we upload the new data.
    gsutil -q rm ${BIFROST_GS_URL}/index.html || true

    echo "Uploading collected bifrost build logs to ${BIFROST_LOG_URL}"

    if [[ -d ${WORKSPACE}/logs ]]; then
        pushd ${WORKSPACE}/logs &> /dev/null
        for x in *.log; do
            echo "Compressing and uploading $x"
            gsutil -q cp -Z ${x} ${BIFROST_GS_URL}/${x}
        done
        popd &> /dev/null
    fi

    echo "Generating the ${BIFROST_LOG_URL}/index.html landing page"
    cat > ${WORKSPACE}/index.html <<EOF
<html>
<h1>Build results for <a href=https://$GERRIT_NAME/#/c/$GERRIT_CHANGE_NUMBER/$GERRIT_PATCHSET_NUMBER>$GERRIT_NAME/$GERRIT_CHANGE_NUMBER/$GERRIT_PATCHSET_NUMBER</a></h1>
<h2>Job: <a href=${BUILD_URL}>$JOB_NAME</a></h2>
<ul>
<li><a href=${BIFROST_LOG_URL}/build_log.txt>build_log.txt</a></li>
EOF

    if [[ -d ${WORKSPACE}/logs ]]; then
        pushd ${WORKSPACE}/logs &> /dev/null
        for x in *.log; do
            echo "<li><a href=${BIFROST_LOG_URL}/${x}>${x}</a></li>" >> ${WORKSPACE}/index.html
        done
        popd &> /dev/null
    fi

    cat >> ${WORKSPACE}/index.html << EOF
</ul>
</html>
EOF

    # Finally, download and upload the entire build log so we can retain
    # as much build information as possible
    echo "Uploading the final console output"
    curl -s -L ${BIFROST_CONSOLE_LOG} > ${WORKSPACE}/build_log.txt
    gsutil -q cp -Z ${WORKSPACE}/build_log.txt ${BIFROST_GS_URL}/build_log.txt
    rm ${WORKSPACE}/build_log.txt

    # Upload landing page
    gsutil -q cp ${WORKSPACE}/index.html ${BIFROST_GS_URL}/index.html
    rm ${WORKSPACE}/index.html
}

function fix_ownership() {
    if [ -z "${JOB_URL+x}" ]; then
        echo "Not running as part of Jenkins. Handle the logs manually."
    else
        # Make sure cache exists
        [[ ! -d ${HOME}/.cache ]] && mkdir ${HOME}/.cache

        sudo chown -R jenkins:jenkins $WORKSPACE
        sudo chown -R jenkins:jenkins ${HOME}/.cache
    fi
}

function cleanup_and_upload() {
    original_exit=$?
    fix_ownership
    upload_logs
    exit $original_exit
}

# check distro to see if we support it
if [[ ! "$DISTRO" =~ (xenial|centos7|suse) ]]; then
    echo "Distro $DISTRO is not supported!"
    exit 1
fi

# remove previously cloned repos
/bin/rm -rf $WORKSPACE/bifrost $WORKSPACE/releng

# Fix up permissions
fix_ownership

# clone all the repos first and checkout the patch afterwards
git clone https://git.openstack.org/openstack/bifrost $WORKSPACE/bifrost
git clone https://gerrit.opnfv.org/gerrit/releng $WORKSPACE/releng

# checkout the patch
cd $CLONE_LOCATION
git fetch $PROJECT_REPO $GERRIT_REFSPEC && sudo git checkout FETCH_HEAD

# combine opnfv and upstream scripts/playbooks
/bin/cp -rf $WORKSPACE/releng/prototypes/bifrost/* $WORKSPACE/bifrost/

# cleanup remnants of previous deployment
cd $WORKSPACE/bifrost
sudo -H -E ./scripts/destroy-env.sh

# provision 3 VMs; xcimaster, controller, and compute
cd $WORKSPACE/bifrost
./scripts/bifrost-provision.sh

# list the provisioned VMs
cd $WORKSPACE/bifrost
source env-vars
ironic node-list
sudo -H -E virsh list
