.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) 2017 ZTE Corp.


.. toctree::
   :maxdepth: 2

=========
Framework
=========

**Test Results Collector of OPNFV Test Projects**:

This project aims to provide a common way of gathering all the test results for OPNFV
testing projects into a single place, and a unified way of getting those results for
testing analysis projects, such as Reporting/Bitergia Dashboard/Qtip. It exposes
Restful APIs for collecting results and pushing them into a MongoDB database.

If you are interested in how TestAPI looks like, please visit OPNFV's official `TestAPI Server`__

.. __: http://testresults.opnfv.org/test

Pre-requsites
=============

TestAPI leverages MongoDB as the data warehouse, in order to let it work
successfully, a MongoDB must be provided, the official MongoDB version in OPNFV
TestAPI is 3.2.6. And the database is **test_results_collection**, the five
collections are *users/pods/projects/testcases/scenarioes/results*. And thanks to
MongoDB's very user-friendly property, they don't need to be created in advance.

Running locally
===============

Requirements
^^^^^^^^^^^^

All requirements are listed in requirements.txt and should be
installed by 'pip install':

    *pip install -r requirements.txt*

Installation
^^^^^^^^^^^^

    *python setup.py install*

After installation, configuration file etc/config.ini will be put under
/etc/opnfv_testapi/. And all the web relevant files under 3rd_party/static
will be in /user/local/share/opnfv_testapi as a totality.

Start Server
^^^^^^^^^^^^

    *opnfv-testapi [--config-file <config.ini>]*

If --config-file is provided, the specified configuration file will be employed
when starting the server, or else /etc/opnfv_testapi/config.ini will be utilized
by default.

After executing the command successfully, a TestAPI server will be started on
port 8000, to visit web portal, please access http://hostname:8000

Regarding swagger-ui website, please visit http://hostname:8000/swagger/spec.html

Running with container
======================

TestAPI has already containerized, the docker image is opnfv/testapi:latest.

**Running the container not behind nginx:**

.. code-block:: shell

    docker run -dti --name testapi -p expose_port:8000
        -e "mongodb_url=mongodb://mongodb_ip:27017/"
        -e "base_url=http://host_name:expose_port"
        opnfv/testapi:latest

**Running the container behind nginx:**

.. code-block:: shell

    docker run -dti --name testapi -p expose_port:8000
        -e "mongodb_url=mongodb://mongodb_ip:27017/"
        -e "base_url=http://nginx_url"
        opnfv/testapi:latest

Unittest & pep8
===============

All requirements for unit tests are outlined in test-requirements.txt, and in TestAPI project, tox is leveraged to drive the executing of unit tests and pep8 check

**Running unit tests**

    *tox -e py27*

**Running pep8 check**

    *tox -e pep8*
