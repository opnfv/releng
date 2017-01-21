#!/bin/bash

set -o errexit

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
pip install -r $WORKSPACE/utils/test/testapi/requirements.txt

find . -type f -name "*.pyc" -delete

nosetests --with-xunit \
          --with-coverage \
          --cover-erase \
          --cover-tests \
	  --cover-package=$WORKSPACE/utils/test/testapi/opnfv_testapi \
          --cover-xml \
          --cover-html \
            $WORKSPACE/utils/test/testapi/opnfv_testapi/tests/

exit_code=$?

deactivate

exit $exit_code
