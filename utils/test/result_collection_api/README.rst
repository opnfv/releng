=============
opnfv-testapi
=============

Test Results Collector of OPNFV Test Projects

Start Server
==============

Getting setup
^^^^^^^^^^^^^

Requirements for opnfv-testapi:

* tornado
* epydoc

These requirements are expressed in the requirements.txt file and may be
installed by running the following (from within a virtual environment)::

    pip install -r requirements.txt

How to install
^^^^^^^^^^^^^^

From within your environment, just run:

    ./install.sh

How to run
^^^^^^^^^^

From within your environment, just run:

    opnfv-testapi

This will start a server on port 8000.  Just visit http://localhost:8000

For swagger website, just visit http://localhost:8000/swagger/spec.html

Unittest
=====================

Getting setup
^^^^^^^^^^^^^

Requirements for unittest:

* testtools
* discover
* futures

These requirements are expressed in the test-requirements.txt file and may be
installed by running the following (from within a virtual environment)::

    pip install -r test-requirements.txt

How to run
^^^^^^^^^^

From within your environment, just run::

    bash run_test.sh

