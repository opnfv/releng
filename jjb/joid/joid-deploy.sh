#!/bin/bash
set +e
set -o nounset

PWD_FILENAME="passwords.sh"

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
fi

##
## Set Joid pod config name
##
    case $NODE_NAME in
        orange-fr-pod2)
            POD=orange-pod2 ;;
        *)
            POD=$NODE_NAME ;;
    esac
    export POD_DC=$(echo $POD |cut -d\- -f1)
    export POD_NUM=$(echo $POD |cut -d\- -f2)
    export POD_NAME=$POD_DC$POD_NUM

##
## Redeploy MAAS or recover the previous config
##

cd $WORKSPACE/ci
if [ -e "$LAB_CONFIG/environments.yaml" ] && [ "$MAAS_REINSTALL" == "false" ]; then
    echo "------ Recover Juju environment to use MAAS ------"
    cp $LAB_CONFIG/environments.yaml .
else
    MAASCONFIG=$WORKSPACE/ci/maas/$POD_DC/$POD_NUM/deployment.yaml
    echo "------ Set MAAS password ------"
    if [ -n "$MAAS_USER" ]; then
        sed -i -- "s/user: ubuntu/user: $MAAS_USER/" $MAASCONFIG
    fi
    if [ -n "$MAAS_PASSWORD" ]; then
        sed -i -- "s/password: ubuntu/password: $MAAS_PASSWORD/" $MAASCONFIG
    fi
    echo "------ Redeploy MAAS ------"
    ./02-maasdeploy.sh $POD_NAME
    RES=$?
    if [ $RES != 0 ]; then
        echo "MAAS Deploy FAILED"
        exit $RES
    fi
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
if [ -n "$OS_ADMIN_PASSWORD" ]; then
    sed -i -- "s/\"admin-password\": openstack/\"admin-password\": $OS_ADMIN_PASSWORD/" $SRCBUNDLE
fi

echo "------ Set ceph disks ------"
if [ -z "$CEPH_DISKS_CONTROLLERS" ]; then
    CEPH_DISKS_CONTROLLERS=$CEPH_DISKS
fi
#Find the first line of osd-devices to change the one for ceph, then the other for ceph-osd
CEPH_DEV_LINE=$(grep -nr osd-devices $SRCBUNDLE |head -n1|cut -d: -f1)
sed -i -- "${CEPH_DEV_LINE}s@osd-devices: /srv@osd-devices: $CEPH_DISKS@" $SRCBUNDLE
sed -i -- "s@osd-devices: /srv@osd-devices: $CEPH_DISKS_CONTROLERS@" $SRCBUNDLE
sed -i -r -- "s/^(\s+osd-reformat: )'no'/\1'$CEPH_REFORMAT'/" $SRCBUNDLE

##
## Configure Joid deployment
##

echo "------ Deploy with juju ------"
echo "Execute: ./deploy.sh -t $HA_MODE -o $OS_RELEASE -s $SDN_CONTROLLER -l $POD_NAME"

./deploy.sh -t $HA_MODE -o $OS_RELEASE -s $SDN_CONTROLLER -l $POD_NAME
RES=$?
if [ $RES != 0 ]; then
    echo "Deploy FAILED"
    exit $RES
fi

##
## Set Admin RC
##
JOID_ADMIN_OPENRC=$LAB_CONFIG/admin-openrc
echo "------ Create OpenRC file [$JOID_ADMIN_OPENRC] ------"
KEYSTONE=$(cat bundles.yaml |shyaml get-value openstack-phase2.services.keystone.options.vip)

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
RES=$?
if [ $RES == 0 ]; then
    echo "Deploy SUCCESS"
else
    echo "Deploy FAILED to auth to openstack"
fi
exit $RES
