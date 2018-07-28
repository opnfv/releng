#!/bin/bash
set -x

# log info to console
echo "Starting the deployment on baremetal environment using $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

echo 1 > /proc/sys/vm/drop_caches

export CONFDIR=$WORKSPACE/deploy/conf
if [[ "$BRANCH" = 'stable/danube' ]]; then
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

    export ISO_URL=file://$BUILD_DIRECTORY/compass.iso
else
    export ISO_URL=file://$BUILD_DIRECTORY/compass.tar.gz
fi

cd $WORKSPACE

export OS_VERSION=${COMPASS_OS_VERSION}
export OPENSTACK_VERSION=${COMPASS_OPENSTACK_VERSION}

if [[ "${DEPLOY_SCENARIO}" =~ "-ocl" ]]; then
    export NETWORK_CONF_FILE=network_ocl.yml
elif [[ "${DEPLOY_SCENARIO}" =~ "-odl" ]]; then
    export NETWORK_CONF_FILE=network_odl.yml
elif [[ "${DEPLOY_SCENARIO}" =~ "-onos" ]]; then
    export NETWORK_CONF_FILE=network_onos.yml
elif [[ "${DEPLOY_SCENARIO}" =~ "-openo" ]]; then
    export NETWORK_CONF_FILE=network_openo.yml
elif [[ "${DEPLOY_SCENARIO}" =~ "-ovs_dpdk" ]]; then
    export NETWORK_CONF_FILE=network_dpdk.yml
else
    export NETWORK_CONF_FILE=network.yml
fi

if [[ "$NODE_NAME" =~ "-virtual" ]]; then
    export NETWORK_CONF=$CONFDIR/vm_environment/$NODE_NAME/${NETWORK_CONF_FILE}
    export DHA_CONF=$CONFDIR/vm_environment/${DEPLOY_SCENARIO}.yml
    if [[ "${DEPLOY_SCENARIO}" =~ "-moon-noha" ]]; then
        export VIRT_NUMBER=3
    elif [[ "${DEPLOY_SCENARIO}" =~ "-noha" ]]; then
        export VIRT_NUMBER=2
    fi
else
    if [[ "$NODE_NAME" =~ "intel-pod17" ]]; then
        export INSTALL_NIC=eno2
    else
        export INSTALL_NIC=eth1
    fi
    export NETWORK_CONF=$CONFDIR/hardware_environment/$NODE_NAME/${NETWORK_CONF_FILE}
    export DHA_CONF=$CONFDIR/hardware_environment/$NODE_NAME/${DEPLOY_SCENARIO}.yml
fi

export DHA=${DHA_CONF}
export NETWORK=${NETWORK_CONF}

source ./ci/deploy_ci.sh

if [ $? -ne 0 ]; then
    echo "depolyment failed!"
    deploy_ret=1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"

exit $deploy_ret
