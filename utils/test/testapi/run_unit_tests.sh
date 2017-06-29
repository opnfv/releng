#!/bin/bash

set -o errexit

# Get script directory
SCRIPTDIR=`dirname $0`

echo "Running unit tests..."

# Creating virtual environment
if [ ! -z $VIRTUAL_ENV ]; then
    venv=$VIRTUAL_ENV
else
    venv=$SCRIPTDIR/.venv
    virtualenv $venv
fi
source $venv/bin/activate

# Install requirements
pip install -r $SCRIPTDIR/requirements.txt
pip install -r $SCRIPTDIR/test-requirements.txt

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
