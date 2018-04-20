.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. (c) Open Platform for NFV Project, Inc. and its contributors


Abstract:
========

This document is temporary, eventually we will have a document that covers all LFN projects.

The jenkins-sandbox instance’s purpose is to allow projects to test their JJB setups before merging their code into the releng repository. It is configured similarly to the master instance, although it cannot publish artifacts or vote in Gerrit.

Uploading a job to sandbox.opnfv.org
------------------------------------

Get JJB:
  ``git clone https://git.openstack.org/openstack-infra/jenkins-job-builder``
  ``cd jenkins-job-builder/``
  ``virtualenv .venv``
  ``source .venv/bin/activate``
  ``pip install -r test-requirements.txt -e . ``
  ``$ jenkins-jobs --version``
  ``Jenkins Job Builder version: 2.0.6``

#note you should edit test-requirements.txt and downgrade to version 2.0.3

create a jenkins.ini (later referenced as --conf ~/jenkins_jobs.ini)

  ``[jenkins]``
  ``user=lfid``
  ``password=password``
  ``url=https://sandbox.opnfv.org``

Modify a job
------------

In this example I have added a job in jjb/releng/opnfv-utils.yml called new-job I am including the required defaults with
  ``jjb/global/releng-macros.yml:jjb/global/releng-defaults.yml``
  and the file that contains the modifed job at the end with
  ``:jjb/releng/opnfv-utils.yml``

Only push one job at a time please, this means you must include the final parameter (job name)
job names that are parameterized must be expaneded eg: job-{branch) must become job-master

test:
``(.venv) jenkins-jobs --conf ~/jenkins_jobs.ini test \
  -r jjb/global/releng-macros.yml:jjb/global/releng-defaults.yml:jjb/releng/opnfv-utils.yml new-job``

deploy:
``(.venv) jenkins-jobs --conf ~/jenkins_jobs.ini update \
  -r jjb/global/releng-macros.yml:jjb/global/releng-defaults.yml:jjb/releng/opnfv-utils.yml new-job ``
