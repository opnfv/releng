.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. (c) Open Platform for NFV Project, Inc. and its contributors

.. _release-automation:

==================
Release Automation
==================

This page describes how projects can take advantage of the release
automation introduced in Fraser for creating their stable branch, and
stable branch Jenkins jobs.

It also describes the structures of the ``releases`` directory and the
associated scripts.

Stable Branch Creation
----------------------

If your project participated in the last release (beginning with
Euphrates), perform the following steps:

#. Copy your project's release file to the new release directory. For
   example::

     cp releases/euphrates/apex.yaml releases/fraser/apex.yaml

#. For projects who are participating the in the stable release process for
   the first time, you can either copy a different project's file and
   changing the values to match your project, or use the following
   template, replacing values marked with ``<`` and ``>``:

   .. code-block:: yaml

       ---
       project: <opnfv-project-name>
       project-type: <opnfv-project-type>
       release-model: stable

       branches:
         - name: stable/<release>
           location:
             <project-repo>: <git-sha1>

#. Modify the file, replacing the previous stable branch name with the
   new release name, and the commit the branch will start at. For
   example:

   .. code-block:: yaml

     branches:
       - name: stable/fraser
         location:
           apex: <git-full-sha1>

#. If your project contains multiple repositories, add them to the list
   of branches. They can also be added later if more time is needed
   before the stable branch window closes.

   .. code-block:: yaml

     branches:
       - name: stable/fraser
         location:
           apex: <git-sha1>
       - name: stable/fraser
         location:
           apex-puppet-tripleo: <git-sha1>

#. Git add, commit, and git-review the changes. A job will be triggered
   to verify the commit exists on the branch, and the yaml file follows
   the scheme listed in ``releases/schema.yaml``

#. Once the commit has been reviewed and merged by Releng, a job will
   be triggered to create the stable branch Jenkins jobs under
   ``jjb/``.


Stable Release Tagging
----------------------

TBD

Release File Fields
-------------------

The following is a description of fields in the Release file, which are
verified by the scheme file at ``releases/schema.yaml``

project
  Project team in charge of the release.

release-model
  Release model the project follows.

  One of: stable, non-release

project-type
  Classification of project within OPNFV.

  One of: installer, feature, testing, tools, infra

upstream
  (Optional) Upstream OpenStack project assocated with this project.

releases
  List of released versions for the project.

  version
    Version of the release, must be in the format ``opnfv-X.Y.Z``.

  location
    Combination of repository and git hash to locate the release
    version.

    Example::

        opnfv-project: f15d50c2009f1f865ac6f4171347940313727547

branches
   List of stable branches for projects following the ``stable`` release-model.

   name
     Stable branch name. Must start with the string ``stable/``

   location
     Same syntax as ``location`` under ``releases``

release-notes
   Link to release notes for the projects per-release.


Scripts
-------

* ``create_branch.py -f <RELEASE_FILE>``

  Create branches in Gerrit listed in the release file.

  Must be ran from the root directory of the releng repository as the
  release name is extracted from the subdirectory under ``releases/``

  The Gerrit server can be changed by creating a ``~/releases.cfg``
  file with the following content::

    [gerrit]
    url=http://gerrit.example.com

  This will override the default configuration of using the OPNFV
  Gerrit server at https://gerrit.opnfv.org, and is primarily used for
  testing.

* ``create_jobs.py -f <RELEASE_FILE>``

  Modifies the jenkins job files for a project to add the stable branch
  stream. Assumes the jenkins jobs are found in the releng repository
  under ``jjb/<project>/``

* ``verify_schema -s <SCHEMA_FILE> -y <YAML_FILE>``

  Verifies the yaml file matches the specified jsonschema formatted
  file. Used to verify the release files under ``releases/``
