#!/bin/bash
set +e
set -o nounset

JOID_LOCAL_CONFIG_FOLDER=$HOME/joid_config
JOID_ADMIN_OPENRC=$JOID_LOCAL_CONFIG_FOLDER/admin-openrc

##
## Load local config or defaults
##

if [ -e "$JOID_LOCAL_CONFIG_FOLDER/config.sh" ]; then
    echo "------ Load local config ------"
    source $JOID_LOCAL_CONFIG_FOLDER/config.sh
else
    echo "------ No local config, load default ------"
    # link NODE_NAME to joid node config names
    case $NODE_NAME in
        orange-fr-pod2)
            POD=orange-pod2 ;;
        *)
            POD=$NODE_NAME ;;
    esac
    export POD_DC=$(echo $POD |cut -d\- -f1)
    export POD_NUM=$(echo $POD |cut -d\- -f2)
    export POD_NAME=$POD_DC$POD_NUM
    export MAAS_REINSTALL=true
    export MAAS_USER=ubuntu
    export MAAS_PASSWORD=ubuntu
    export OS_ADMIN_PASSWORD=openstack
    export CEPH_DISKS=/srv
    export CEPH_REFORMAT=no
fi

##
## Redeploy MAAS or recover the previous config
##

cd $WORKSPACE/ci
if [ -e "$JOID_LOCAL_CONFIG_FOLDER/environments.yaml" ] && [ "$MAAS_REINSTALL" == "false" ]; then
    echo "------ Recover Juju environment to use MAAS ------"
    cp $JOID_LOCAL_CONFIG_FOLDER/environments.yaml .
else
    MAASCONFIG=$WORKSPACE/ci/maas/$POD_DC/$POD_NUM/deployment.yaml
    echo "------ Set MAAS password ------"
    sed -i -- "s/user: ubuntu/user: $MAAS_USER/" $MAASCONFIG
    sed -i -- "s/password: ubuntu/password: $MAAS_PASSWORD/" $MAASCONFIG
    echo "------ Redeploy MAAS ------"
    ./02-maasdeploy.sh $POD_NAME
fi

##
## Configure Joid deployment
##

# Get juju deployer file
if [ "$HA_MODE" == 'nonha' ]; then
    SRCBUNDLE=$WORKSPACE/ci/$SDN_CONTROLLER/juju-deployer/ovs-$SDN_CONTROLLER.yaml
else
    SRCBUNDLE=$WORKSPACE/ci/$SDN_CONTROLLER/juju-deployer/ovs-$SDN_CONTROLLER-$HA_MODE.yaml
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
echo "Execute: ./deploy.sh -t $HA_MODE -o $OS_RELEASE -s $SDN_CONTROLLER -l $POD_NAME"

./deploy.sh -t $HA_MODE -o $OS_RELEASE -s $SDN_CONTROLLER -l $POD_NAME

##
## Set Admin RC
##

echo "------ Create OpenRC file [$JOID_ADMIN_OPENRC] ------"
KEYSTONE=$(cat bundles.yaml |shyaml get-value openstack-phase2.services.keystone.options.vip)

# create the folder if needed
JOID_ADMIN_OPENRC_FOLDER=$(echo $JOID_ADMIN_OPENRC | perl -pe "s|^(.*/).*?$|\1|")
if [ ! -d "$JOID_ADMIN_OPENRC_FOLDER" ]; then
    mkdir -p $JOID_ADMIN_OPENRC_FOLDER
fi

# export the openrc file
cat << EOF > $JOID_ADMIN_OPENRC
export OS_USERNAME=admin
export OS_PASSWORD=$OS_ADMIN_PASSWORD
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://$KEYSTONE:5000/v2.0
export OS_REGION_NAME=Canonical
EOF

##
## Backup local juju env
##

if [ -d "$JOID_LOCAL_CONFIG_FOLDER" ]; then
    echo "------ Backup Juju environment ------"
    cp environments.yaml $JOID_LOCAL_CONFIG_FOLDER/
fi

##
## Basic test to return a realistic result to jenkins
##
source $JOID_ADMIN_OPENRC
curl -i -sw '%{http_code}' -H "Content-Type: application/json"   -d "
{ \"auth\": {
    \"identity\": {
      \"methods\": [\"password\"],
      \"password\": {
        \"user\": {
          \"name\": \"$OS_TENANT_NAME\",
          \"domain\": { \"id\": \"default\" },
          \"password\": \"$OS_PASSWORD\"
        }
      }
    }
  }
}"   http://$KEYSTONE:5000/v3/auth/tokens |grep "HTTP/1.1 20" 2>&1 >/dev/null; echo $?;
RES=$?
if [ $RES == 0 ]; then
    echo "Deploy SUCCESS"
else
    echo "Deploy FAILED"
fi
return $RES
