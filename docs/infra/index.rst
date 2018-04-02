.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. (c) Open Platform for NFV Project, Inc. and its contributors

.. _software-infrastructure:

=======================
Software Infrastructure
=======================

OPNFV Software Infrastructure consists of set of components and tools that
realize OPNFV Continuous Integration (CI) and provide means for community to
contribute to OPNFV in most efficient way. OPNFV Software Infrastructure
enables and orchestrates  development, integration and testing activities for
the components OPNFV consumes from upstream communities and for the development
work done in scope of OPNFV. Apart from orchestration aspects, providing timely
feedback that is fit for purpose to the OPNFV community is one of its missions.

CI is the top priority for OPNFV Software Infrastructure. Due to the importance
the OPNFV community puts into it, the resulting CI machinery is highly
powerful, capable and runs against distributed hardware infrastructure managed
by OPNFV Pharos_ Project. The hardware infrastructure OPNFV CI relies on is
located in 3 different continents, 5+ different countries and 10+ different
member companies.

OPNFV CI is continuously evolved in order to fulfill the needs and match the
expectations of the OPNFV community.

OPNFV Software Infrastructure is developed, maintained and operated by OPNFV
Releng_ Project with the support from Linux Foundation.

Continuous Integration Server
-----------------------------

Jenkins

.. toctree::
   :maxdepth: 1

   jenkins/connect-to-jenkins
   jenkins/user-guide
   jenkins/jjb-usage
   jenkins/labels

Source Control and Code Review
------------------------------

Gerrit

.. toctree::
   :maxdepth: 1

   gerrit/user-guide

Artifact and Image Repositories
-------------------------------

Google Storage & Docker Hub

.. toctree::
   :maxdepth: 1

   artifacts/index
   artifacts/docker-hub


Issue and Bug Tracking
----------------------

JIRA

.. toctree::
   :maxdepth: 1

   jira/user-guide


Dashboards and Analytics
------------------------

  - `Pharos Dashboard`_

  - `Test Results`_

  - `Bitergia Dashboard`_


.. _Pharos: https://wiki.opnfv.org/display/pharos/Pharos+Home
.. _Releng: https://wiki.opnfv.org/display/releng/Releng

.. _Bitergia Dashboard: https://opnfv.biterg.io/
.. _Pharos Dashboard: https://labs.opnfv.org/
.. _Test Results: https://testresults.opnfv.org/
