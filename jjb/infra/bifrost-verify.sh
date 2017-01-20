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

    echo "Uploading build logs to ${BIFROST_LOG_URL}"

    echo "Uploading console output"
    curl -s -L ${BIFROST_CONSOLE_LOG} > build_log.txt
    gsutil -q cp -Z build_log.txt ${BIFROST_GS_URL}/build_log.txt
    rm build_log.txt

    [[ ! -d ${WORKSPACE}/logs ]] && exit 0

    pushd ${WORKSPACE}/logs/ &> /dev/null
    for x in *.log; do
        echo "Compressing and uploading $x"
        gsutil -q cp -Z ${x} ${BIFROST_GS_URL}/${x}
    done

    echo "Generating the landing page"
    cat > index.html <<EOF
<html>
<h1>Build results for <a href=https://$GERRIT_NAME/#/c/$GERRIT_CHANGE_NUMBER/$GERRIT_PATCHSET_NUMBER>$GERRIT_NAME/$GERRIT_CHANGE_NUMBER/$GERRIT_PATCHSET_NUMBER</a></h1>
<h2>Job: $JOB_NAME</h2>
<ul>
<li><a href=${BIFROST_LOG_URL}/build_log.txt>build_log.txt</a></li>
EOF

    for x in *.log; do
        echo "<li><a href=${BIFROST_LOG_URL}/${x}>${x}</a></li>" >> index.html
    done

    cat >> index.html << EOF
</ul>
</html>
EOF

    gsutil -q cp index.html ${BIFROST_GS_URL}/index.html

    rm index.html

    popd &> /dev/null
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
if [[ ! "$DISTRO" =~ (trusty|centos7|suse) ]]; then
    echo "Distro $DISTRO is not supported!"
    exit 1
fi

# remove previously cloned repos
sudo /bin/rm -rf /opt/bifrost /opt/puppet-infracloud /opt/stack /opt/releng

# Fix up permissions
fix_ownership

# clone all the repos first and checkout the patch afterwards
sudo git clone https://git.openstack.org/openstack/bifrost /opt/bifrost
sudo git clone https://git.openstack.org/openstack-infra/puppet-infracloud /opt/puppet-infracloud
sudo git clone https://gerrit.opnfv.org/gerrit/releng /opt/releng

# checkout the patch
cd $CLONE_LOCATION
sudo git fetch $PROJECT_REPO $GERRIT_REFSPEC && sudo git checkout FETCH_HEAD

# combine opnfv and upstream scripts/playbooks
sudo /bin/cp -rf /opt/releng/prototypes/bifrost/* /opt/bifrost/

# place bridge creation file on the right path
sudo mkdir -p /opt/puppet-infracloud/files/elements/infra-cloud-bridge/static/opt
sudo cp /opt/puppet-infracloud/templates/bifrost/create_bridge.py.erb /opt/puppet-infracloud/files/elements/infra-cloud-bridge/static/opt/create_bridge.py

# replace bridge name
sudo sed -i s/"<%= @bridge_name -%>"/br_opnfv/g /opt/puppet-infracloud/files/elements/infra-cloud-bridge/static/opt/create_bridge.py

# cleanup remnants of previous deployment
cd /opt/bifrost
sudo -E ./scripts/destroy-env.sh

# provision 3 VMs; jumphost, controller, and compute
cd /opt/bifrost
sudo -E ./scripts/test-bifrost-deployment.sh

# list the provisioned VMs
cd /opt/bifrost
source env-vars
ironic node-list
virsh list
