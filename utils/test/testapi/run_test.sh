#!/bin/bash

set -o errexit

# Get script directory
BASEDIR=$(dirname "$0")

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
pip install -r $BASEDIR/requirements.txt

find . -type f -name "*.pyc" -delete

nosetests --with-xunit \
          --with-coverage \
          --cover-erase \
          --cover-package=$BASEDIR/opnfv_testapi/cmd \
	  --cover-package=$BASEDIR/opnfv_testapi/commonn \
	  --cover-package=$BASEDIR/opnfv_testapi/resources \
	  --cover-package=$BASEDIR/opnfv_testapi/router \
          --cover-xml \
          --cover-html \
            $BASEDIR/opnfv_testapi/tests

exit_code=$?

deactivate

exit $exit_code
