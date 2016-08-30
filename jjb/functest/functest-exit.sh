#!/bin/bash

branch=${GIT_BRANCH##*/}
ret_val_file="${HOME}/opnfv/functest/results/${branch}/return_value"
if [ ! -f ${ret_val_file} ]; then
    echo "Return value not found!"
    exit -1
fi

ret_val=`cat ${ret_val_file}`
if [[ ${ret_val} == 0 ]]; then
    exit 0
else
    exit -1
fi
