.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) 2017 ZTE Corporation


********
Overview
********

TestAPI uses Python as primary programming language and build the framework from the following packages

======== ===============================================================================================================
Module   Package
======== ===============================================================================================================
api      `Tornado-Motor`_ - API applications using Motor with tornado
swagger  `tornado-swagger`_ - a wrapper for tornado which enables swagger-ui-v1.2 support
web      `angular`_ - a superheroic JavaScript MVW framework, the version is AngularJS v1.3.15
docs     `sphinx`_ - a tool that makes it easy to create intelligent and beautiful documentation
testing  `pytest`_ - a mature full-featured Python testing tool that helps you write better programs
======== ===============================================================================================================


Source Code
===========

The structure of repository is based on the recommended sample in `The Hitchhiker's Guide to Python`_

==========================  ====================================================================================================
Path                        Content
==========================  ====================================================================================================
``./3rd_party/``            third part included in TestAPI project
``./docker/``               configuration for building Docker image for TestAPI deployment
``./docs/``                 user and developer documentation, design proposals
``./etc/``                  configuration files used to install opnfv-testapi
``./opnfv_testapi/``        the actual package
``./opnfv_testapi/tests/``  package functional and unit tests
``./opts/``                 optional components, e.g. one click deployment script
==========================  ====================================================================================================


Coding Style
============

TestAPI follows `OpenStack Style Guidelines`_ for source code and commit message.

Specially, it is recommended to link each patch set with a JIRA issue. Put::

    JIRA: RELENG-n

in commit message to create an automatic link.


Testing
=======

All testing related code are stored in ``./opnfv_testapi/tests/``

==================  ====================================================================================================
Path                Content
==================  ====================================================================================================
``./tests/unit/``   unit test for each module, follow the same layout as ./opnfv_testapi/
``./conftest.py``   pytest configuration in project scope
==================  ====================================================================================================

`tox`_ is used to automate the testing tasks

.. code-block:: shell

    cd <project_root>
    pip install tox
    tox

The test cases are written in `pytest`_. You may run it selectively with

.. code-block:: shell

    pytest opnfv_testapi/tests/unit/common/test_config.py


Branching
=========

Currently, no branching for TestAPI, only master branch


Releasing
=========

Currently, TestAPI does not follow community's milestones and releases

.. _Tornado-Motor: https://motor.readthedocs.io/en/stable/tutorial-tornado.html
.. _tornado-swagger: https://github.com/SerenaFeng/tornado-swagger
.. _angular: https://code.angularjs.org/1.3.15/docs/guide
.. _sphinx: http://www.sphinx-doc.org/en/stable/
.. _pytest: http://doc.pytest.org/
.. _OpenStack Style Guidelines: http://docs.openstack.org/developer/hacking/
.. _The Hitchhiker's Guide to Python: http://python-guide-pt-br.readthedocs.io/en/latest/writing/structure/
.. _tox: https://tox.readthedocs.io/
