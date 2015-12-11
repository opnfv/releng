#!/bin/bash
set +e

####### Temporary - to be done with jenkins params #####
JOID_MODE=ha
JOID_RELEASE=liberty
JOID_LOCAL_CONFIG_FOLDER=~/joid_config
JOID_SDN_CONTROLLER=odl
#################

##
## Load local config or defaults
##

if [ -e "$JOID_LOCAL_CONFIG_FOLDER/config.sh" ]
    then
        echo "------ Load local config ------"
        source $JOID_LOCAL_CONFIG_FOLDER/config.sh
    else
        echo "------ No local config, load default ------"
        # SOME TO BE SET BY JENKINS IN THE NEXT RELEASES
        export POD_DC=intel
        export POD_NUM=pod5
        export POD_NAME=\$POD_DC\$POD_NUM
        export MAAS_REINSTALL=true
        export MAAS_USER=ubuntu
        export MAAS_PASSWORD=ubuntu
        export OS_ADMIN_PASSWORD=openstack
        export CEPH_DISKS=/srv
        export CEPH_REFORMAT=no
        export JOID_ADMIN_OPENRC=$WORKSPACE/admin_openrc.sh
fi

##
## Redeploy MAAS or recover the previous config
##

cd $WORKSPACE/ci
if [ -e "$JOID_LOCAL_CONFIG_FOLDER/environments.yaml" ] && [ "z$MAAS_REINSTALL" == "zfalse" ]
    then
        echo "------ Recover Juju environment to use MAAS ------"
        cp $JOID_LOCAL_CONFIG_FOLDER/environments.yaml .
    else
        MAASCONFIG=$WORKSPACE/ci/maas/$POD_DC/$POD_NUM/deployment.yaml
        echo "------ Set MAAS password ------"
        sed -i -- 's/user: ubuntu/user: $MAAS_USER/' $MAASCONFIG
        sed -i -- 's/password: ubuntu/password: $MAAS_PASSWORD/' $MAASCONFIG
        echo "------ Redeploy MAAS ------"
        ./02-maasdeploy.sh $POD_NAME
fi

##
## Configure Joid deployment
##

# Get juju deployer file
if [ "$JOID_MODE" == 'nonha' ]
    then SRCBUNDLE=$WORKSPACE/ci/$JOID_SDN_CONTROLLER/juju-deployer/ovs-$JOID_SDN_CONTROLLER.yaml
    else SRCBUNDLE=$WORKSPACE/ci/$JOID_SDN_CONTROLLER/juju-deployer/ovs-$JOID_SDN_CONTROLLER-$JOID_MODE.yaml
fi

# Modify files

echo "------ Set openstack password ------"
sed -i -- "s/\"admin-password\": openstack/\"admin-password\": $OS_ADMIN_PASSWORD/" $SRCBUNDLE

echo "------ Set ceph disks ------"
sed -i -- "s@osd-devices: /srv@osd-devices: $CEPH_DISKS@" $SRCBUNDLE
sed -i -r -- "s/^(\s+osd-reformat: )'no'/\1'$CEPH_REFORMAT'/" $SRCBUNDLE

##
## Configure Joid deployment
##

echo "------ Deploy with juju ------"
echo "Execute: ./deploy.sh -t $JOID_MODE -o $JOID_RELEASE -s $JOID_SDN_CONTROLLER -l $POD_NAME"

./deploy.sh -t $JOID_MODE -o $JOID_RELEASE -s $JOID_SDN_CONTROLLER -l $POD_NAME

##
## Set Admin RC
##

echo "------ Create OpenRC file ------"
KEYSTONE=$(cat bundle.yaml |shyaml get-value openstack-phase2.services.keystone.options.vip)

cat << EOF > $JOID_ADMIN_OPENRC
export OS_USERNAME=admin
export OS_PASSWORD=$OS_ADMIN_PASSWORD
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://$KEYSTONE:5000/v2.0
export OS_REGION_NAME=Canonical
EOF

if [ -d "$JOID_LOCAL_CONFIG_FOLDER" ]
    then
        echo "------ Backup Juju environment ------"
        cp environments.yaml $JOID_LOCAL_CONFIG_FOLDER/
fi
