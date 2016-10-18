#! /bin/bash

# Before run this script, make sure that testtools and discover
# had been installed in your env
# or else using pip to install them as follows:
# pip install testtools, discover

find . -type f -name "*.pyc" -delete
testrargs="discover ./opnfv_testapi/tests/unit"
python -m testtools.run $testrargs
