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

--------------
Baremetal PODs
--------------

Baremetal PODs are used to deploy OPNFV on to baremetal hardware through
one of the installer projects. They enable the full range of scenarios
to be deployed and tested.

~~~~~~~~~~~~~~~~~~~~~~~~~~~
Baremetal PODs Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order of a POD to be considered CI-Ready the following requirements
must be met:

  #. Pharos Compliant and has a PDF
  #. Connected to Jenkins
  #. 24/7 Uptime
  #. No Development
  #. No manual intervention

------------
Virtual PODS
------------

Virtual PODs are used to deploy OPNFV in a virtualized environment
generally on top of KVM through libvirt.

~~~~~~~~~~~~
Requirements
~~~~~~~~~~~~

 #. Have required virtualization packages installed
 #. Meet the Pharos resource specification for virtual PODs
 #. Connected to Jenkins
 #. 24/7 Uptime

-------------
Build Servers
-------------

Build servers are used to build project, run basic verifications (such
as unit tests and linting), and generate documentation.

~~~~~~~~~~~~
Requirements
~~~~~~~~~~~~

 #. Have required `packages_` installed
 #. 24/7 Uptime
 #. Connected to Jenkins

.. _packages: https://wiki.opnfv.org/display/INF/Continuous+Integration#ContinuousIntegration-BuildServers
