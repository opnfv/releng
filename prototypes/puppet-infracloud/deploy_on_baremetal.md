How to deploy Infra Cloud on baremetal
==================================

Install bifrost controller
--------------------------
First step for deploying Infra Cloud is to install the bifrost controller. This can be virtualized, doesn't need to be on baremetal.
To achieve that, first we can create a virtual machine with libvirt, with the proper network setup. This VM needs to share one physical interface (the PXE boot one), with the servers for the controller and compute nodes.
Please follow documentation on: [https://git.openstack.org/cgit/openstack/bifrost/tree/tools/virsh_dev_env/README.md](https://git.openstack.org/cgit/openstack/bifrost/tree/tools/virsh_dev_env/README.md) to get sample templates and instructions for creating the bifrost VM.

Once the **baremetal** VM is finished, you can login by ssh and start installing bifrost there. To proceed, follow this steps:

 1. Change to root user, install git
 2. Clone releng project (cd /opt, git clone https://gerrit.opnfv.org/gerrit/releng)
 3. cd /opt/releng/prototypes/puppet-infracloud
 4. Copy hiera to the right folder (cp hiera/common_baremetal.yaml /var/lib/hiera/common.yaml)
 5. Ensure hostname is properly set ( hostnamectl set-hostname baremetal.opnfvlocal , hostname -f )
 6. Install puppet and modules ( ./install_puppet.sh , ./install_modules.sh )
 7. Apply puppet to install bifrost (puppet apply manifests/site.pp --modulepath=/etc/puppet/modules:/opt/releng/prototypes/puppet-infracloud/modules)

 With these steps you will have a bifrost controller up and running.

Deploy baremetal servers
--------------------------
Once you have bifrost controller ready, you need to use it to start deployment of the baremetal servers.
On the same bifrost VM, follow these steps:

 1. Source bifrost env vars: source /opt/stack/bifrost/env-vars
 2. Export baremetal servers inventory:  export BIFROST_INVENTORY-SOURCE=/opt/stack/baremetal.json 
 3. Enroll the servers: ansible-playbook -vvv -i inventory/bifrost_inventory.py enroll-dynamic.yaml -e @/etc/bifrost/bifrost_global_vars
 4. Deploy the servers:  ansible-playbook -vvv -i inventory/bifrost_inventory.py deploy-dynamic.yaml -e @/etc/bifrost/bifrost_global_vars
 5. Wait until they are on **active** state, check it with: ironic node-list

In case of some server needing to be redeployed, you can reset it and redeploy again with:

 1. ironic node-set-provision-state <name_of_server> deleted
 2. Wait and check with ironic node-list until the server is on **available** state
 3. Redeploy again: ansible-playbook -vvv -i inventory/bifrost_inventory.py deploy-dynamic.yaml -e @/etc/bifrost/bifrost_global_vars

Deploy baremetal servers
--------------------------
Once all the servers are on **active** state, they can be accessed by ssh and InfraCloud manifests can be deployed on them, to properly deploy a controller and a compute.
On each of those, follow that steps:

 1. ssh from the bifrost controller to their external ips: ssh root@172.30.13.90
 2. cd /opt, clone releng project (git clone https://gerrit.opnfv.org/gerrit/releng)
 3. Copy hiera to the right folder ( cp hiera/common_baremetal.yaml /var/lib/hiera/common.yaml)
 4. Install modules: ./install_modules.sh
 5. Apply puppet: puppet apply manifests/site.pp --modulepath=/etc/puppet/modules:/opt/releng/prototypes/puppet-infracloud/modules

Once this has been done on controller and compute, you will have a working cloud. To start working with it, follow that steps:

 1. Ensure that controller00.opnfvlocal resolves properly to the external IP (this is already done in the bifrost controller)
 2. Copy releng/prototypes/puppet-infracloud/creds/clouds.yaml to $HOME/.config/openstack/clouds.yaml
 3. Install python-openstackclient
 4. Specify the cloud you want to use: export OS_CLOUD=opnfvlocal
 5. Now you can start operating in your cloud with openstack-client: openstack flavor list

