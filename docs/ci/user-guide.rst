.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. (c) Open Platform for NFV Project, Inc. and its contributors

.. _ci-user-guide:

=============
CI User Guide
=============

Structure of the Releng Repository
----------------------------------

jjb/<projects>
   Individual project CI configurations.

jjb/global
   Collection of JJB defaults and templates shared by all projects.

global-jjb/
   Git submodule pointing to `Global-JJB`_, which provides a variety of
   common `CI jobs`_ such as ReadTheDocs
   (RTD) builds.

docs/
  This documentation.

releases/
  Release configuration files for creating stable branches and tagging
  repositories and related automation scripts.

utils/
  Collection of common utilities used by projects

utils/build-server-ansible
  Ansible configuration for managing build servers. This is where
  projects can add packages they need for their CI to the servers.


CI Setup
--------

Basic Setup
~~~~~~~~~~~

All projects are required to have a **+1 Verified** vote in Gerrit in
order to merge their code. As a new project that comes in may not yet
know how they want to setup CI, they can pass this validation by
configuring a 'no-op' job to run against their changesets.

1. Clone the `Releng`_ repository, using the *Clone with commit-msg
   hook* command under the *SSH* tab (displayed after logging in and
   uploading an SSH key):

   .. note::
     <gerrit username> in the command below will be your username in
     Gerrit when viewing the command on the website.

   For example::

     git clone "ssh://<gerrit username>@gerrit.opnfv.org:29418/releng" && \
     scp -p -P 29418 <gerrit username>@gerrit.opnfv.org:hooks/commit-msg "releng/.git/hooks/"


2. Create a project directory under the *jjb/* directory, and an intial
   project YAML file::

     mkdir jjb/myproject
     touch jjb/myproject/myproject-ci-jobs.yaml

3. Modify the project YAML file to add the basic validation job::

     $EDITOR jjb/myproject/myproject-ci-jobs.yaml

   ::

     ---
     - project:
         name: myproject
         project:
           - '{name}'
         jobs:
           - '{project}-verify-basic'

Docker Builds
~~~~~~~~~~~~~

Docker build are managed through the **jjb/releng/opnfv-docker.yaml**
file. Modify this file with your project details to enable docker builds
on merges and tags to your project repository::

  ---
  - project:
      name: opnfv-docker'

      [...]

      dockerrepo:
        [...]
        - 'myproject':
          project: 'myproject'
          <<: *master


Documentation Builds
~~~~~~~~~~~~~~~~~~~~

Documentation is build using they Python Sphinx project. You can read
more about how these build work and how your documentation should be
setup in the `opnfvdocs`_ project.

Create a file at **jjb/myproject/myproject-rtd-builds.yaml** with the
following content::

  ---
  - project:
      name: myproject-rtd
      project: myproject
      project-name: myproject

      project-pattern: 'myproject'
      rtd-build-url: <request from LFN IT>
      rtd-token: <request from LFN IT>

      jobs:
        - '{project-name}-rtd-jobs'

.. note::
   Open a ticket with a link to the change adding your documentation
   at `support.linuxfoundation.org`_ and the LFN IT team will
   provide you the *rtd-build-url* and *rtd-token*.

This will create jobs to build your project documentation (under *docs/*
in your project repository) on proposed changes, and trigger a rebuild
on the RTD site when code is merged in your project.

.. _Jenkins Job Builder: https://docs.openstack.org/infra/jenkins-job-builder/
.. _Releng: https://gerrit.opnfv.org/gerrit/admin/repos/releng
.. _Global-JJB: https://docs.releng.linuxfoundation.org/projects/global-jjb/en/latest/index.html
.. _CI jobs: https://docs.releng.linuxfoundation.org/projects/global-jjb/en/latest/index.html#global-jjb-templates
.. _opnfvdocs: https://docs.opnfv.org/en/latest/how-to-use-docs/index.html
.. _support.linuxfoundation.org: https://jira.linuxfoundation.org/plugins/servlet/theme/portal/2/create/145
