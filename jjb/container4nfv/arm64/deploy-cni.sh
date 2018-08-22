#!/bin/bash -e

cd container4nfv/src/arm/cni-deploy

DEPLOY_SCENARIO={scenario}

virtualenv .venv
source .venv/bin/activate
pip install ansible==2.6.1

ansible-playbook -i inventory/inventory.cfg deploy.yml --tags flannel,multus

if [ "$DEPLOY_SCENARIO" == "k8-sriov-nofeature-noha" ]; then
    ansible-playbook -i inventory/inventory.cfg deploy.yml --tags sriov
elif [ "$DEPLOY_SCENARIO" == "k8-vpp-nofeature-noha" ]; then
    ansible-playbook -i inventory/inventory.cfg deploy.yml --tags vhost-vpp
fi
