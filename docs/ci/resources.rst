.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. (c) Open Platform for NFV Project, Inc. and its contributors

.. _ci-resources:

============
CI Resources
============

CI for OPNFV requires a range of resources in order to meet testing and
verification needs. Each resource must meet a set of criteria in order
to be part of CI for an OPNFV release. There are three types of
resources:

- Baremetal PODs (PODs)
- Virtual PODs (vPODs)
- Build Servers


.. _ci-resources-baremetal-pods:

Baremetal PODs
--------------

Baremetal PODs are used to deploy OPNFV on to baremetal hardware through
one of the installer projects. They enable the full range of scenarios
to be deployed and tested.

**Requirements**

In order of a POD to be considered CI-Ready the following requirements
must be met:

#. Pharos Compliant and has a PDF
#. Connected to Jenkins
#. 24/7 Uptime
#. No Development
#. No manual intervention

.. include:: tables/ci-baremetal-servers.rst


.. _ci-resources-virtual-pods:

Virtual PODs
------------

Virtual PODs are used to deploy OPNFV in a virtualized environment
generally on top of KVM through libvirt.

**Requirements**

#. Have required virtualization packages installed
#. Meet the Pharos resource specification for virtual PODs
#. Connected to Jenkins
#. 24/7 Uptime

.. include:: tables/ci-virtual-servers.rst

.. _ci-resources-build-servers:

Build Servers
-------------

Build servers are used to build project, run basic verifications (such
as unit tests and linting), and generate documentation.

**Requirements**

#. Have required `packages_` installed
#. 24/7 Uptime
#. Connected to Jenkins

.. include:: tables/ci-build-servers.rst


.. _ci-resources-dev-servers:

CI Resources Labels
-------------------

:ci-resource:

 Resource devoted to CI

:ci-pod:

 POD devoted to CI

:opnfv-build:

 Node is for builds - independent of OS

:opnfv-build-centos:

 Node is for builds needing CentOS

:opnfv-build-centos-arm:

 Node is for ARM builds on CentOS

:opnfv-build-ubuntu:

 Node is for builds needing Ubuntu

:opnfv-build-ubuntu-arm:

 Node is for ARM builds on Ubuntu

:{installer}-baremetal:

 POD is devoted to {installer} for baremetal
 deployments

:{installer}-virtual:

 Server is devoted to {installer} for virtual
 deployments


.. _dev-resources:

=====================
Development Resources
=====================

.. include:: tables/none-ci-servers.rst

.. _arm-contact: foo@example.com
.. _ericsson-contact: bar@example.com
.. _Trevor Bramwell: tbramwell@linuxfoundation.org
.. _lf-build1: https://build.opnfv.org/ci/computer/lf-build1/
.. _lf-build2: https://build.opnfv.org/ci/computer/lf-build2/
.. _packages: https://wiki.opnfv.org/display/INF/Continuous+Integration#ContinuousIntegration-BuildServers
