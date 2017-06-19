###########################
OPNFV XCI Developer Sandbox
###########################

The XCI Developer Sandbox is created by the OPNFV community for the OPNFV
community in order to

- provide means for OPNFV developers to work with OpenStack master branch,
  cutting the time it takes to develop new features significantly and testing
  them on OPNFV Infrastructure
- enable OPNFV developers to identify bugs earlier, issue fixes faster, and
  get feedback on a daily basis
- establish mechanisms to run additional testing on OPNFV Infrastructure to
  provide feedback to OpenStack community
- make the solutions we put in place available to other LF Networking Projects
  OPNFV works with closely

More information about OPNFV XCI and the sandbox can be seen on
`OPNFV Wiki <https://wiki.opnfv.org/pages/viewpage.action?pageId=8687635>`_.

===================================
Components of XCI Developer Sandbox
===================================

The sandbox uses OpenStack projects for VM node creation, provisioning
and OpenStack installation.

- **openstack/bifrost:** Bifrost (pronounced bye-frost) is a set of Ansible
  playbooks that automates the task of deploying a base image onto a set
  of known hardware using ironic. It provides modular utility for one-off
  operating system deployment with as few operational requirements as
  reasonably possible. Bifrost supports different operating systems such as
  Ubuntu, CentOS, and openSUSE.
  More information about this project can be seen on
  `Bifrost documentation <https://docs.openstack.org/developer/bifrost/>`_.

- **openstack/openstack-ansible:** OpenStack-Ansible is an official OpenStack
  project which aims to deploy production environments from source in a way
  that makes it scalable while also being simple to operate, upgrade, and grow.
  More information about this project can be seen on
  `OpenStack Ansible documentation <https://docs.openstack.org/developer/openstack-ansible/>`_.

- **opnfv/releng:** OPNFV Releng Project provides additional scripts, Ansible
  playbooks and configuration options in order for developers to have easy
  way of using openstack/bifrost and openstack/openstack-ansible by just
  setting couple of environment variables and executing a single script.
  More infromation about this project can be seen on
  `OPNFV Releng documentation <https://wiki.opnfv.org/display/releng>_`.

==========
Basic Flow
==========

Here are the steps that take place upon the execution of the sandbox script
``xci-deploy.sh``:

1. Sources environment variables in order to set things up properly.
2. Installs ansible on the host where sandbox script is executed.
3. Creates and provisions VM nodes based on the flavor chosen by the user.
4. Configures the host where the sandbox script is executed.
5. Configures the deployment host which the OpenStack installation will
   be driven from.
6. Configures the target hosts where OpenStack will be installed.
7. Configures the target hosts as controller(s) and compute(s) nodes.
8. Starts the OpenStack installation.

=====================
Sandbox Prerequisites
=====================

In order to use this sandbox, the host must have certain packages installed.

- libvirt
- python
- pip
- git
- <fix the list with all the dependencies>
- passwordless sudo

The host must also have enough CPU/RAM/Disk in order to host number of VM
nodes that will be created based on the chosen flavor. See the details from
`this link <https://wiki.opnfv.org/display/INF/XCI+Developer+Sandbox#XCIDeveloperSandbox-Prerequisites>`_.

===========================
Flavors Provided by Sandbox
===========================

OPNFV XCI Sandbox provides different flavors such as all in one (aio) which
puts much lower requirements on the host machine and full-blown HA.

* aio: Single node which acts as the deployment host, controller and compute.
* mini: One deployment host, 1 controller node and 1 compute node.
* noha: One deployment host, 1 controller node and 2 compute nodes.
* ha: One deployment host, 3 controller nodes and 2 compute nodes.

See the details of the flavors from
`this link <https://wiki.opnfv.org/display/INF/XCI+Developer+Sandbox#XCIDeveloperSandbox-AvailableFlavors>`_.

==========
How to Use
==========

Basic Usage
-----------

clone OPNFV Releng repository

    git clone https://gerrit.opnfv.org/gerrit/releng.git

change into directory where the sandbox script is located

    cd releng/prototypes/xci

execute sandbox script

    ./xci-deploy.sh

Issuing above command will start aio sandbox deployment and the sandbox
should be ready between 1,5 and 2 hours depending on the host machine.

Please remember that the user executing the XCI script will need to
have an ssh key available, and stored in $HOME/.ssh directory.
You can generate one by executing

    ssh-keygen -t rsa

Advanced Usage
--------------

The flavor to deploy, the versions of upstream components to use can
be configured by developers by setting certain environment variables.
Below example deploys noha flavor using the latest of openstack-ansible
master branch and stores logs in different location than what is configured.

clone OPNFV Releng repository

    git clone https://gerrit.opnfv.org/gerrit/releng.git

change into directory where the sandbox script is located

    cd releng/prototypes/xci

set the sandbox flavor

    export XCI_FLAVOR=noha

set the version to use for openstack-ansible

    export OPENSTACK_OSA_VERSION=master

set where the logs should be stored

    export LOG_PATH=/home/jenkins/xcilogs

execute sandbox script

    ./xci-deploy.sh

===============
User Variables
===============

All user variables can be set from command line by exporting them before
executing the script. The current user variables can be seen from
``releng/prototypes/xci/config/user-vars``.

The variables can also be set directly within the file before executing
the sandbox script.

===============
Pinned Versions
===============

As explained above, the users can pick and choose which versions to use. If
you want to be on the safe side, you can use the pinned versions the sandbox
provides. They can be seen from ``releng/prototypes/xci/config/pinned-versions``.

How Pinned Versions are Determined
----------------------------------

OPNFV runs periodic jobs against upstream projects openstack/bifrost and
openstack/ansible using latest on master and stable/ocata branches,
continuously chasing the HEAD of corresponding branches.

Once a working version is identified, the versions of the upstream components
are then bumped in releng repo.

==================
XCI developer tips
==================

It is possible to run XCI in development mode, in order to test the
latest changes. When deploying on this mode, the script will use the working
directories for releng/bifrost/OSA, instead of cloning the whole repositories
on each run.
To enable it, you need to export the different DEV_PATH vars:

- export OPNFV_RELENG_DEV_PATH=/opt/releng/
- export OPENSTACK_BIFROST_DEV_PATH=/opt/bifrost
- export OPENSTACK_OSA_DEV_PATH=/opt/openstack-ansible

This will cause the deployment to pick the development copies stored at the
specified directories, and use them instead of cloning those on every run.

===========================================
Limitations, Known Issues, and Improvements
===========================================

The list can be seen using `this link <https://jira.opnfv.org/issues/?filter=11616>`_.

=========
Changelog
=========

Changelog can be seen using `this link <https://jira.opnfv.org/issues/?filter=11625>`_.

=======
Testing
=======

Sandbox is continuously tested by OPNFV CI to ensure the changes do not impact
users. In fact, OPNFV CI itself uses the sandbox scripts to run daily platform
verification jobs.

=======
Support
=======

OPNFV XCI issues are tracked on OPNFV JIRA Releng project. If you encounter
and issue or identify a bug, please submit an issue to JIRA using
`this link <https://jira.opnfv.org/projects/RELENG>_`.

If you have questions or comments, you can ask them on ``#opnfv-pharos`` IRC
channel on Freenode.
