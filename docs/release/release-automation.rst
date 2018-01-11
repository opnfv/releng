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


team
  Team in charge of the release.

release-model
  Release model the project follows.

  One of: stable, non-release, ``TBD``, ...

type
  Classification of project within OPNFV.

  One of: installer, testing, tools, ``TBD``, ...

upstream
  (Optional) Upstream OpenStack project assocated with this project.

repos
  List of repositories managed by the project and their associated
  releases.

  releases
    List of releases of the project.

    These are defined by version and git hash, which is tagged in the
    repo.

branches
   List of branches and their initial git hash for projects under the
   stable release-model.

release-notes
   Link to release notes for the projects per-release.

Creating Stable Branch
----------------------

Add the following to your ``releases/<release>/<project>.yaml`` to have
stable branch automatically created. ``<release>`` refers to the current
release and should be written without the inequality signs (ex: ``arno``)


.. code-block:: yaml

    ---

    ...

    branches:
      - name: stable/<release>
        repo: <project-repo>
        location: <git-hash>


Scripts
-------

 * ``create_branch.py -f <RELEASE_FILE>``

   Create branches in Gerrit listed in the release file.

   The Gerrit server can be changed by creating a ``~/releases.cfg``
   file with the following content::

     [gerrit]
     url=http://gerrit.example.com

   This will override the default configuration of using the OPNFV
   Gerrit server at https://gerrit.opnfv.org.
