#!/bin/bash

set -o errexit

# Get script directory
SCRIPTDIR=`dirname $0`

# Either Workspace is set (CI)
if [ -z $WORKSPACE ]
then
    WORKSPACE="."
fi

echo "Running unit tests..."

# Creating virtual environment
virtualenv $WORKSPACE/testapi_venv
source $WORKSPACE/testapi_venv/bin/activate

# Install requirements
pip install -r $SCRIPTDIR/requirements.txt

find . -type f -name "*.pyc" -delete

nosetests --with-xunit \
    --with-coverage \
    --cover-erase \
    --cover-package=$SCRIPTDIR/opnfv_testapi/cmd \
    --cover-package=$SCRIPTDIR/opnfv_testapi/commonn \
    --cover-package=$SCRIPTDIR/opnfv_testapi/resources \
    --cover-package=$SCRIPTDIR/opnfv_testapi/router \
    --cover-xml \
    --cover-html \
    $SCRIPTDIR/opnfv_testapi/tests

exit_code=$?

deactivate

exit $exit_code
