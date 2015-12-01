#!/bin/bash
set +e
source $JOID_LOCAL_CONFIG_FOLDER/config.sh

cd ~/joid/ci
echo "------ Create MAAS and Juju bootstrap ------"
./02-maasdeploy.sh $POD_NAME
