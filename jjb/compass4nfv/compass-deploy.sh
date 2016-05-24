#!/bin/bash
set -x

# log info to console
echo "Starting the deployment on baremetal environment using $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

# source the properties file so we get OPNFV vars
source $BUILD_DIRECTORY/latest.properties

# echo the info about artifact that is used during the deployment
echo "Using ${OPNFV_ARTIFACT_URL/*\/} for deployment"

if [[ ! "$JOB_NAME" =~ (verify|merge) ]]; then
    # for none-merge deployments
    # checkout the commit that was used for building the downloaded artifact
    # to make sure the ISO and deployment mechanism uses same versions
    echo "Checking out $OPNFV_GIT_SHA1"
    git checkout $OPNFV_GIT_SHA1 --quiet
fi

echo 1 > /proc/sys/vm/drop_caches

export CONFDIR=$WORKSPACE/deploy/conf
export ISO_URL=file://$BUILD_DIRECTORY/compass.iso

if [[ "${DEPLOY_SCENARIO}" =~ "-ocl" ]]; then
    export NETWORK_CONF_FILE=network_ocl.yml
else
    export NETWORK_CONF_FILE=network.yml
fi

if [[ "$NODE_NAME" =~ "-virtual" ]]; then
    export NETWORK_CONF=$CONFDIR/vm_environment/$NODE_NAME/${NETWORK_CONF_FILE}
    export DHA_CONF=$CONFDIR/vm_environment/${DEPLOY_SCENARIO}.yml
else
    export INSTALL_NIC=eth1
    export NETWORK_CONF=$CONFDIR/hardware_environment/$NODE_NAME/${NETWORK_CONF_FILE}
    export DHA_CONF=$CONFDIR/hardware_environment/$NODE_NAME/${DEPLOY_SCENARIO}.yml
fi

cd $WORKSPACE

export OS_VERSION=${COMPASS_OS_VERSION}
export OPENSTACK_VERSION=${COMPASS_OPENSTACK_VERSION}
./deploy.sh --dha ${DHA_CONF} --network ${NETWORK_CONF}
if [ $? -ne 0 ]; then
    echo "depolyment failed!"
    deploy_ret=1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"

ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
sshpass -p root scp 2>/dev/null $ssh_options root@${INSTALLER_IP}:/var/ansible/run/openstack_${COMPASS_OPENSTACK_VERSION}-opnfv2/ansible.log ./  &> /dev/null

exit $deploy_ret
