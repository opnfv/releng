#!/bin/bash

echo "--------------------------------------------------------"
echo "This is diasy4nfv deploy job!"
echo "--------------------------------------------------------"

cd $WORKSPACE

if [[ "$NODE_NAME" =~ "-virtual" ]]; then
    export NETWORK_CONF=./deploy/config/vm_environment/$NODE_NAME/network.yml
    export DHA_CONF=./deploy/config/vm_environment/$NODE_NAME/deploy.yml
else
    # TODO: For the time being, we need to pass this script to let contributors merge their work.
    echo "No support for non-virtual node"
    exit 0
fi

sudo ./ci/deploy/deploy.sh -d ${DHA_CONF} -n ${NETWORK_CONF} -p ${NODE_NAME:-"zte-virtual1"}

if [ $? -ne 0 ]; then
    echo "depolyment failed!"
    deploy_ret=1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"

exit $deploy_ret
