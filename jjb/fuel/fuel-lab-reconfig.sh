#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
set -o errexit
set -o nounset
set -o pipefail

# check to see if ucs login info file exists
if [ -e ~/.ssh/ucs_creds ];then
    source ~/.ssh/ucs_creds
else
    echo "Unable to find UCS credentials for LF lab reconfiguration...Exiting"
    exit 1
fi

# clone releng
echo "Cloning releng repo..."
if ! GIT_SSL_NO_VERIFY=true git clone https://gerrit.opnfv.org/gerrit/releng; then
    echo "Unable to clone releng repo...Exiting"
    exit 1
fi

# log info to console
echo "Starting the lab reconfiguration for $INSTALLER_TYPE..."
echo "--------------------------------------------------------"
echo

# create venv
$WORKSPACE/releng/utils/lab-reconfiguration/create_venv.sh

# disable nounset because 'activate' script contains unbound variable(s)
set +o nounset
# enter venv
source $WORKSPACE/releng/utils/lab-reconfiguration/venv/bin/activate
# set nounset back again
set -o nounset

# verify we are in venv
if [[ ! $(which python | grep venv) ]]; then
    echo "Unable to activate venv...Exiting"
    exit 1
fi

python $WORKSPACE/releng/utils/lab-reconfiguration/reconfigUcsNet.py -i $ucs_host -u $ucs_user -p $ucs_password -f $WORKSPACE/releng/utils/lab-reconfiguration/fuel.yaml

# while undergoing reboot
sleep 30

# check to see if slave is back up
ping_counter=0
ping_flag=0
while [ "$ping_counter" -lt 20 ]; do
    if [[ $(ping -c 5 172.30.10.72) ]]; then
        ping_flag=1
        break
    fi
    ((ping_counter++))
    sleep 10
done

if [ "$ping_flag" -eq 1 ]; then
    echo "Slave is pingable, now wait 180 seconds for services to start"
    sleep 180
else
    echo "Slave did not come back up after reboot: please check lf-pod2"
    exit 1
fi

set +o nounset
deactivate

echo
echo "--------------------------------------------------------"
echo "Done!"
