#!/bin/bash

set -o errexit

# Get script directory
SCRIPTDIR=`dirname $0`

echo "Running unit tests..."

# Creating virtual environment
virtualenv $SCRIPTDIR/testapi_venv
source $SCRIPTDIR/testapi_venv/bin/activate

# Install requirements
pip install -r $SCRIPTDIR/requirements.txt
pip install coverage
pip install nose>=1.3.1
pip install pytest

find . -type f -name "*.pyc" -delete

nosetests --with-xunit \
    --with-coverage \
    --cover-erase \
    --cover-package=$SCRIPTDIR/opnfv_testapi/cmd \
    --cover-package=$SCRIPTDIR/opnfv_testapi/common \
    --cover-package=$SCRIPTDIR/opnfv_testapi/resources \
    --cover-package=$SCRIPTDIR/opnfv_testapi/router \
    --cover-xml \
    --cover-html \
    $SCRIPTDIR/opnfv_testapi/tests

exit_code=$?

deactivate

exit $exit_code
