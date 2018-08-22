#!/bin/bash
set -e

cd compass4nfv

export ADAPTER_OS_PATTERN='(?i)CentOS-7.*arm.*'
export OS_VERSION="centos7"
export KUBERNETES_VERSION="v1.9.1"
if [[ "$NODE_NAME" =~ "-virtual" ]]; then
    export DHA="deploy/conf/vm_environment/k8-nosdn-nofeature-noha.yml"
    export NETWORK="deploy/conf/vm_environment/network.yml"
    export VIRT_NUMBER=2 VIRT_CPUS=8 VIRT_MEM=8192 VIRT_DISK=50G
else
    export DHA="deploy/conf/hardware_environment/huawei-pod8/k8-nosdn-nofeature-noha.yml"
    export NETWORK="deploy/conf/hardware_environment/huawei-pod8/network.yml"
fi

./deploy.sh
