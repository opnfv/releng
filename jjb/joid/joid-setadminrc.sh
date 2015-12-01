#!/bin/bash
set +e
source $JOID_LOCAL_CONFIG_FOLDER/config.sh

cat << EOF > $JOID_ADMIN_OPENRC
export OS_USERNAME=admin
export OS_PASSWORD=$OS_ADMIN_PASSWORD
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://192.168.2.23:5000/v2.0
export OS_REGION_NAME=Canonical
EOF
