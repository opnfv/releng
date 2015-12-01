#!/bin/bash
set +e
source $JOID_LOCAL_CONFIG_FOLDER/config.sh
cd ~/joid/ci

# Get juju deployer file
if [ "$JOID_MODE" == 'nonha' ]
    then SRCBUNDLE=~/joid/ci/$JOID_SDN_CONTROLLER/juju-deployer/ovs-$JOID_SDN_CONTROLLER.yaml
    else SRCBUNDLE=~/joid/ci/$JOID_SDN_CONTROLLER/juju-deployer/ovs-$JOID_SDN_CONTROLLER-$JOID_MODE.yaml
    fi

# Get MAAS config file
MAASCONFIG=~/joid/ci/maas/$POD_DC/$POD_NUM/deployment.yaml

# Modify files

echo "------ Set MAAS password ------"
sed -i -- 's/user: ubuntu/user: $MAAS_USER/' $MAASCONFIG
sed -i -- 's/password: ubuntu/user: $MAAS_PASSWORD/' $MAASCONFIG

echo "------ Set openstack password ------"
sed -i -- "s/\"admin-password\": openstack/\"admin-password\": $OS_ADMIN_PASSWORD/" $SRCBUNDLE

echo "------ Set ceph disks ------"
sed -i -- "s/\"osd-devices: \/srv/osd-devices: $CEPH_DISKS/" $SRCBUNDLE
if [ "$CEPH_REFORMAT" == 'true' ]
    then sed -i -- "s/osd-reformat: 'no'/osd-reformat: 'yes'/" $SRCBUNDLE
