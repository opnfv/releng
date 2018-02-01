#!/bin/bash
set -e

cd compass4nfv

export ADAPTER_OS_PATTERN='(?i)CentOS-7.*arm.*'
export OS_VERSION="centos7"
export KUBERNETES_VERSION="v1.7.3"
export DHA="deploy/conf/vm_environment/k8-nosdn-nofeature-noha.yml"
export NETWORK="deploy/conf/vm_environment/network.yml"
export VIRT_NUMBER=2 VIRT_CPUS=2 VIRT_MEM=4096 VIRT_DISK=50G

./deploy.sh
