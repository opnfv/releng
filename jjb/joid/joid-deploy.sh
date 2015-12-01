#!/bin/bash
set +e
source $JOID_LOCAL_CONFIG_FOLDER/config.sh

cd ~/joid/ci
echo "------ Deploy  JOID------"
echo "--- joid mode:           $JOID_MODE"
echo "--- joid release:        $JOID_RELEASE"
echo "--- joid sdn controller: $JOID_SDN_CONTROLLER"
echo "--- pod name:            $POD_NAME"

./deploy.sh -t $JOID_MODE -o $JOID_RELEASE -s $JOID_SDN_CONTROLLER -l $POD_NAM
