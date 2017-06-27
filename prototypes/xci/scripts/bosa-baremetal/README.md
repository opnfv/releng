# Openstack install on baremetal OPNFV pods with OSA and Bifrost

Note 0: This bunch of scripts is not an installer, just a recipe to install
Openstack on an OPNFV pods for developper needs and XCI jobs.

Note 1: The target is only Orange pod1 and pod2 for now

# About the jumphost

The jumphost is a fresh ubuntu 16.04 install with a direct internet connection, and a network interface linked with the openstack br-mgmt network.

This jumphost can be virtual.

The openstack nodes are split in 2: 3 for controllers and 2 for computes

# About log servers

This server is not installed by bifrost today, and is an ubuntu VM
installed closed to the jumphost.

# Prepare inventory file

```inventory``` file intends to be as simple and generic as possible
but must be checked and filled before any other steps

# Prepare baremetal description

Please take a non null time to prepare all config files in vars/ folder.

Today, the baremetal description is done with vars/pods.yaml for the pod
description and vars/servers.yaml for the servers description accross several
pods. **Those files will be replaced by the Pod Description File.**

The vars/defaults.yaml contains all vars not directly related to baremetal.

# Run everything:

The installation is done from the jumphost

(this need to be checked)
./run.sh inventory_pod1_local

# Run manually

The installation is done from the jumphost

## Bifrost

### Prepare the jumphost

```
apt-get install -y software-properties-common python-setuptools \
    python-dev libffi-dev libssl-dev git sshpass tree python-pip
pip install --upgrade pip
pip install cryptography
pip install ansible
```

This jumphost hosts the bifrost server (DNSmasq, pxe, ipmitool...)

### installation

First clone this repo to the jumphost (in /opt or $HOME), then run

```ansible-playbook -i inventory_pod1_local  opnfv-bifrost-install.yaml```


### Generate inventory, config files, enroll and deploy

```ansible-playbook -i inventory_pod1_local opnfv-bifrost-enroll-deploy.yaml```

just check the result using ```ironic node-list```

A the end wait for servers ssh interface to be up: ```bifrost_check_ssh```

## Prepare nodes

```ansible-playbook -i /etc/bosa/ansible_inventory opnfv-prepare-nodes.yaml```

## OSA

### Install

Go back to this repo folder and prepare OSA install:

```ansible-playbook -i inventory_pod1_local  opnfv-osa-prepare.yaml`````

To avoid issues with ansible version installed by OSA, we remove actual ansible

```pip uninstall -y ansible```

Then we run OSA bootstrap

```/opt/openstack-ansible/scripts/bootstrap-ansible.sh ```

### configure

Then configure OSA:

```ansible-playbook -i inventory_pod1_local  opnfv-osa-configure.yaml`````

### run:

For the next steps we follow OSA playbooks (this may be pushed to a playbook):

```
cd /opt/openstack-ansible/playbooks
openstack-ansible setup-hosts.yml
openstack-ansible setup-infrastructure.yml
ansible galera_container -m shell -a "mysql -h localhost -e 'show status like \"%wsrep_cluster_%\";'"
openstack-ansible setup-openstack.yml
```

# Annexes

## Pretty ansible output

just add this environment variable
```export ANSIBLE_STDOUT_CALLBACK=debug```
