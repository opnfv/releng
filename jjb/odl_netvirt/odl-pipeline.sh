#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
RELENG_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
echo "Starting the odl-netvirt pipeline. Doing Task $1"
echo "---------------------------------------------------------------------------------------"
usage() {
        echo "usage: $0 <Task>" >&2
    }
if [[ $# -ne 1 ]]; then
    usage
    exit
fi

if [[ $1 == "download-artifact" ]];then
  # Later it will just get the tarball
  # wget ..

  # At the moment it gets the the whole gerrit branch refspec info etc.,
  # to build it.
  pushd $WORKSPACE/odl-pipeline/lib
    ./odl_builder.sh --branch $GERRIT_BRANCH --refspec $GERRIT_REFSPEC --change_number $GERRIT_CHANGE_NUMBER
  popd
elif [[ $1 == "install-artifact" ]];then
  ./odl_reinstaller.sh --cloner-info ~/cloner-info/ --odl-artifact $ARTIFACT_LOCATION
elif [[ $1 == "run-functest" ]];then
  SSH_KEYS=~/cloner-info/undercloud_ssh/id_rsa
  OPENSTACK_CREDS=~/cloner-info/overcloudrc
  INSTALLER_TYPE='odl-pipeline'
  BUILD_TAG='virtual'
  INSTALLER_IP='None'
  FUNCTEST_SUITE_NAME='??'
  # This is the functest branch
  GIT_BRANCH='master'
  pushd $RELENG_DIR/../functest/
    ./functest-cleanup.sh
    ./set-functest-env.sh
    ./functest-suite.sh
  popd
elif [[ $1 == "postprocess" ]];then
fi