.. _release-automation

Release Automation
==================

Describes the way the '/releases' directory works for Releng: structure,
how to add a project, how to create stable-branch, how to add a release.

Release File
------------

Each project participating in a release should create a file under
``releases/<release>`` using their project name. This will will be used
to track the branches, artifacts, and tags needed for the release.

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


Creating Stable Branch
----------------------

Add the following to your ``releases/<release>/<project>.yaml`` to have
stable branch automatically created. ``<release>`` refers to the current
release and should be written without the inequality signs (ex: ``arno``)


.. code-block:: yaml

    ---
    project: opnfv-project-name
    project-type: opnfv-project-type

    ...

    branches:
      - name: stable/<release>
        location:
          <project-repo>: <git-hash>


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
