#!/bin/bash

ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
if [ ! -f ${ret_val_file} ]; then
    echo "Return value not found!"
    exit -1
fi

ret_val=`cat ${ret_val_file}`

exit ${ret_val}
