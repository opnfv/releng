#!/bin/bash
set -e

dest_path="$HOME/admin.conf"

if [[ "${DEPLOY_SCENARIO:0:2}" == "k8" ]];then
    juju scp kubernetes-master/0:config "${dest_path}"
fi
