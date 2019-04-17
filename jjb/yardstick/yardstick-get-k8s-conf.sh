#!/bin/bash
set -e

dest_path="$HOME/admin.conf"

if [[ "${DEPLOY_SCENARIO:0:2}" == "k8" ]];then
    if [[ ${INSTALLER_TYPE} == 'joid' ]];then
        juju scp kubernetes-master/0:config "${dest_path}"
    elif [[ ${INSTALLER_TYPE} == 'compass' ]];then
        echo "Copy admin.conf to ${dest_path}"
        docker cp compass-tasks:/opt/admin.conf "${dest_path}"
    elif [[ ${INSTALLER_TYPE} == 'fuel' ]];then
        echo "Getting kubernetes config ..."
        docker cp -L fuel:/opt/kubernetes.config "${dest_path}"
    fi
fi
