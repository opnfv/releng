# Openstack install on baremetal OPNFV pods with OSA and bifrost

Note 0: This bunch of scripts is not an installer, just a recipe to install
Openstack on an OPNFV pods for developper needs and XCI jobs.

Note 1: The target is only Orange pod1 and pod2 for now

# About the jumphost

The jumphost is a fresh ubuntu 16.04 install with a direct internet connection,
and a network interface linked with the openstack br-mgmt network.

This jumphost can be virtual.

The openstack nodes are split in 2: 3 for controllers and 2 for computes

# About log servers

This server is not installed by bifrost today, and is an ubuntu VM
installed closed to the jumphost.

# Prepare baremetal description

Please take a non null time to prepare all config files in vars/ folder.

Today, the baremetal description is done with vars/pods.yaml for the pod
description and vars/servers.yaml for the servers description accross several
pods. **Those files will be replaced by the Pod Description File.**

The vars/defaults.yaml contains all vars not directly related to baremetal.


# Bifrost

This jumphost hosts the bifrost server (DNSmasq, pxe, ipmitool...)

## installation

First clone this repo to the jumphost (in /opt or $HOME), then run

```ansible-playbook -vvv opnfv-bifrost-install.yaml```


## Generate inventory, and config files

```ansible-playbook -vvv opnfv-bifrost-enroll-deploy.yaml```


## Enroll and deploy

change folder and go to bifrost playbooks

```cd /opt/bifrost/playbooks```

set inventory file

```export BIFROST_INVENTORY_SOURCE=$HOME/bifrost_inventory.json```

Enroll

```ansible-playbook -vvvv -i inventory/bifrost_inventory.pyenroll-dynamic.yaml```

and finally deploy

```ansible-playbook -vvvv -i inventory/bifrost_inventory.py deploy-dynamic.yaml```

just check the result using ```ironic node-list```

A the end wait for servers ssh interface to be up: ```bifrost_check_ssh```

# OSA

## Install

Go back to this repo folder and prepare OSA install:

```ansible-playbook opnfv-osa-install.yaml```

Run bootstrap manually:

```/opt/openstack-ansible/scripts/bootstrap-ansible.sh```

Then prepare OSA config file:

```ansible-playbook opnfv-osa-configure.yaml```

For the next steps we follow OSA playbooks (this may be pushed to a playbook):

```
cd /opt/openstack-ansible/playbooks
openstack-ansible setup-hosts.yml
openstack-ansible setup-infrastructure.yml
ansible galera_container -m shell \
  -a "mysql -h localhost -e 'show status like \"%wsrep_cluster_%\";'"
openstack-ansible setup-openstack.yml
```

# Annexes

## Pretty ansible output

just add this environment variable
```export ANSIBLE_STDOUT_CALLBACK=debug```
