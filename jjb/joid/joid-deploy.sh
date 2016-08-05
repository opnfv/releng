#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Orange and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set +e
set -o nounset

PWD_FILENAME="passwords.sh"

##
##
##
function exit_on_error {
    RES=$1
    MSG=$2
    if [ $RES != 0 ]; then
        echo "FAILED - $MSG"
        exit $RES
    fi
}


##
## Create LAB_CONFIG folder if not exists
##
mkdir -p $LAB_CONFIG

##
## Override default passwords with local settings if needed
##

if [ -e "$LAB_CONFIG/$PWD_FILENAME" ]; then
    echo "------ Load local passwords ------"
    source $LAB_CONFIG/$PWD_FILENAME
else
    export MAAS_USER=ubuntu
    export MAAS_PASSWORD=ubuntu
    export OS_ADMIN_PASSWORD=openstack
fi

##
## Set Joid pod config name
##
    # This part will be removed when pod names will be synced between jenkins and joid config
    case $NODE_NAME in
        *virtual*)
            POD=default ;;
        *)
            POD=$NODE_NAME ;;
    esac
    export POD_NAME=${POD/-}

##
## Parse Network config
##

EXTERNAL_NETWORK=${EXTERNAL_NETWORK:-}
# split EXTERNAL_NETWORK=name;type;first ip;last ip; gateway;network
IFS=';' read -r -a EXTNET <<< "$EXTERNAL_NETWORK"
EXTNET_NAME=${EXTNET[0]}
EXTNET_TYPE=${EXTNET[1]}
EXTNET_FIP=${EXTNET[2]}
EXTNET_LIP=${EXTNET[3]}
EXTNET_GW=${EXTNET[4]}
EXTNET_NET=${EXTNET[5]}

##
## Redeploy MAAS or recover the previous config
##

cd $WORKSPACE/ci
if [ -e "$LAB_CONFIG/environments.yaml" ] && [ "$MAAS_REINSTALL" == "false" ]; then
    echo "------ Recover Juju environment to use MAAS ------"
    cp $LAB_CONFIG/environments.yaml .
else
    MAASCONFIG=$WORKSPACE/ci/maas/${POD/-*}/${POD/*-}/deployment.yaml
    echo "------ Set MAAS password ------"
    sed -i -- "s/user: ubuntu/user: $MAAS_USER/" $MAASCONFIG
    sed -i -- "s/password: ubuntu/password: $MAAS_PASSWORD/" $MAASCONFIG
    echo "------ Redeploy MAAS ------"
    ./00-maasdeploy.sh $POD_NAME
    exit_on_error $? "MAAS Deploy FAILED"
fi

##
## Configure Joid deployment
##

# Based on scenario naming we can get joid options
# naming convention:
#    os-<controller>-<nfvfeature>-<mode>[-<extrastuff>]
# With parameters:
#    controller=(nosdn|odl_l3|odl_l2|onos|ocl)
#       No odl_l3 today
#    nfvfeature=(kvm|ovs|dpdk|nofeature)
#       '_' list separated.
#    mode=(ha|noha)
#    extrastuff=(none)
#       Optional field - Not used today

IFS='-' read -r -a DEPLOY_OPTIONS <<< "${DEPLOY_SCENARIO}--"
#last -- need to avoid nounset error

SDN_CONTROLLER=${DEPLOY_OPTIONS[1]}
NFV_FEATURES=${DEPLOY_OPTIONS[2]}
HA_MODE=${DEPLOY_OPTIONS[3]}
EXTRA=${DEPLOY_OPTIONS[4]}

if [ "$SDN_CONTROLLER" == 'odl_l2' ] || [ "$SDN_CONTROLLER" == 'odl_l3' ]; then
    SDN_CONTROLLER='odl'
fi
if [ "$HA_MODE" == 'noha' ]; then
    HA_MODE='nonha'
fi
SRCBUNDLE="${WORKSPACE}/ci/${SDN_CONTROLLER}/juju-deployer/"
SRCBUNDLE="${SRCBUNDLE}/ovs-${SDN_CONTROLLER}-${HA_MODE}.yaml"


# Modify Bundle
echo "------ Set openstack password ------"
sed -i -- "s/admin-password: openstack/admin-password: $OS_ADMIN_PASSWORD/" $SRCBUNDLE

if [ -n "$EXTNET_NAME" ]; then
    echo "------ Set openstack default network ------"
    sed -i -- "s/neutron-external-network: ext_net/neutron-external-network: $EXTNET_NAME/" $SRCBUNDLE
fi

echo "------ Set ceph disks ------"
#Find the first line of osd-devices to change the one for ceph, then the other for ceph-osd
sed -i -- "s@osd-devices: /srv@osd-devices: $CEPH_DISKS@" $SRCBUNDLE
sed -i -r -- "s/^(\s+osd-reformat: )'no'/\1'$CEPH_REFORMAT'/" $SRCBUNDLE

# temporary sfc feature is availble only on onos and trusty
if [ "$NFV_FEATURES" == 'sfc' ] && [ "$SDN_CONTROLLER" == 'onos' ];then
    UBUNTU_DISTRO=trusty
fi

##
## Configure Joid deployment
##

echo "------ Deploy with juju ------"
echo "Execute: ./deploy.sh -t $HA_MODE -o $OS_RELEASE -s $SDN_CONTROLLER -l $POD_NAME -d $UBUNTU_DISTRO -f $NFV_FEATURES"

./deploy.sh -t $HA_MODE -o $OS_RELEASE -s $SDN_CONTROLLER -l $POD_NAME -d $UBUNTU_DISTRO -f $NFV_FEATURES
exit_on_error $? "Main deploy FAILED"

##
## Set Admin RC
##
JOID_ADMIN_OPENRC=$LAB_CONFIG/admin-openrc
echo "------ Create OpenRC file [$JOID_ADMIN_OPENRC] ------"

# get Keystone ip
case "$HA_MODE" in
    "ha")
        KEYSTONE=$(cat bundles.yaml |shyaml get-value openstack-phase1.services.keystone.options.vip)
        ;;
    *)
        KEYSTONE=$(juju status keystone |grep public-address|sed -- 's/.*\: //')
        ;;
esac


# get controller IP
case "$SDN_CONTROLLER" in
    "odl")
        SDN_CONTROLLER_IP=$(juju status odl-controller/0 |grep public-address|sed -- 's/.*\: //')
        ;;
    "onos")
        SDN_CONTROLLER_IP=$(juju status onos-controller/0 |grep public-address|sed -- 's/.*\: //')
        ;;
    *)
        SDN_CONTROLLER_IP='none'
        ;;
esac
SDN_PASSWORD='admin'

# export the openrc file
cat << EOF > $JOID_ADMIN_OPENRC
export OS_USERNAME=admin
export OS_PASSWORD=$OS_ADMIN_PASSWORD
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://$KEYSTONE:35357/v2.0
export OS_REGION_NAME=RegionOne
export OS_ENDPOINT_TYPE='adminURL'
export CINDER_ENDPOINT_TYPE='adminURL'
export GLANCE_ENDPOINT_TYPE='adminURL'
export KEYSTONE_ENDPOINT_TYPE='adminURL'
export NEUTRON_ENDPOINT_TYPE='adminURL'
export NOVA_ENDPOINT_TYPE='adminURL'
export SDN_CONTROLLER=$SDN_CONTROLLER_IP
export SDN_PASSWORD=$SDN_PASSWORD
export OS_INTERFACE=admin
EOF

##
## Backup local juju env
##

echo "------ Backup Juju environment ------"
cp environments.yaml $LAB_CONFIG/

##
## Basic test to return a realistic result to jenkins
##

echo "------ Do basic test ------"
source $JOID_ADMIN_OPENRC
curl -i -sw '%{http_code}' -H "Content-Type: application/json"   -d "
{ \"auth\": {
    \"identity\": {
      \"methods\": [\"password\"],
      \"password\": {
        \"user\": {
          \"name\": \"admin\",
          \"domain\": { \"id\": \"default\" },
          \"password\": \"$OS_ADMIN_PASSWORD\"
        }
      }
    }
  }
}"   http://$KEYSTONE:5000/v3/auth/tokens |grep "HTTP/1.1 20" 2>&1 >/dev/null;
exit_on_error $? "Deploy FAILED to auth to openstack"

##
## Exit success
##

echo "Deploy success"
exit 0
