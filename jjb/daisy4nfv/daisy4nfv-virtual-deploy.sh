#!/bin/bash

echo "--------------------------------------------------------"
echo "This is diasy4nfv virtual deploy job!"
echo "--------------------------------------------------------"

cd $WORKSPACE

if [[ "$NODE_NAME" =~ "-virtual" ]]; then
    export NETWORK_CONF=./deploy/config/vm_environment/$NODE_NAME/network.yml
    export DHA_CONF=./deploy/config/vm_environment/$NODE_NAME/deploy.yml
else
    echo "No support for non-virtual node"
    exit 0
fi

./ci/deploy/deploy.sh ${DHA_CONF} ${NETWORK_CONF}

if [ $? -ne 0 ]; then
    echo "depolyment failed!"
    deploy_ret=1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"

exit $deploy_ret
