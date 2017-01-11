#!/bin/bash

# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# Stop opnfv-testapi server
proc_number=`ps -ef | grep opnfv-testapi | grep -v grep | wc -l`

if [ $proc_number -gt 0 ]; then
    procs=`ps -ef | grep opnfv-testapi | grep -v grep`
    echo "Kill opnfv-testapi server $procs"
    ps -ef | grep opnfv-testapi | grep -v grep | awk '{print $2}' | xargs kill -kill &>/dev/null
fi

deactivate
