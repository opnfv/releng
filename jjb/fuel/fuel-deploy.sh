#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# source the file so we get OPNFV vars
source latest.properties

# echo the info about artifact that is used during the deployment
echo "Using $(echo $OPNFV_ARTIFACT_URL | cut -d'/' -f3) for deployment"

# create TMPDIR if it doesn't exist
export TMPDIR=$HOME/tmpdir
mkdir -p $TMPDIR

# change permissions down to TMPDIR
chmod a+x $HOME
chmod a+x $TMPDIR

# set CONFDIR, BRIDGE
POD_CONF_DIR=$WORKSPACE/deploy/templates/hardware_environment/conf/linux_foundation_lab/pod2
BRIDGE=pxebr

# clone genesis repo and checkout the SR1 tag
#echo "Cloning genesis repo"
#cd $WORKSPACE
#GIT_SSL_NO_VERIFY=true git clone https://gerrit.opnfv.org/gerrit/genesis genesis
#cd genesis
#git checkout arno.2015.2.0

# cleanup first
#sudo $WORKSPACE/genesis/common/ci/clean.sh -base_config $WORKSPACE/genesis/foreman/ci/inventory/lf_pod2_ksgen_settings.yml

# prepare for Fuel Deployment
#sudo $WORKSPACE/genesis/common/ci/setup.sh

# log info to console
echo "Starting the deployment using $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

# start the deployment
echo "Issuing command"
echo "sudo $WORKSPACE/ci/deploy.sh -iso $WORKSPACE/opnfv.iso -dea $POD_CONF_DIR/dea.yaml -dha $POD_CONF_DIR/dha.yaml -s $TMPDIR -b $BRIDGE -nh"

sudo $WORKSPACE/ci/deploy.sh -iso $WORKSPACE/opnfv.iso -dea $POD_CONF_DIR/dea.yaml -dha $POD_CONF_DIR/dha.yaml -s $TMPDIR -b $BRIDGE -nh

echo
echo "--------------------------------------------------------"
echo "Done!"
