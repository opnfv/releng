.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. (c) Open Platform for NFV Project, Inc. and its contributors

.. _ci-overview:

========
OPNFV CI
========

OPNFV continuous integration (CI) is ran on a variety of :doc:`hardware <resources>`
connected to Jenkins and mangaged through YAML files in the `Releng`_
repository. These YAML files are read by `Jenkins Job Builder`_ to
generate and upload Jenkins jobs to the server. See the :doc:`User Guide
<user-guide>` for resources on getting started with CI for your project.

.. toctree::
   :maxdepth: 2

   user-guide
   resources

.. _Releng: https://gerrit.opnfv.org/gerrit/admin/repos/releng
.. _Jenkins Job Builder: https://docs.openstack.org/infra/jenkins-job-builder/
