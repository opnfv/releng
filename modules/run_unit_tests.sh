#!/bin/bash
set -o errexit
set -o pipefail

# Either Workspace is set (CI)
if [ -z $WORKSPACE ]
then
    WORKSPACE="."
fi


# ***************
# Run unit tests
# ***************
echo "Running unit tests..."

# start vitual env
virtualenv $WORKSPACE/modules_venv
source $WORKSPACE/modules_venv/bin/activate

# install python packages
easy_install -U setuptools
easy_install -U pip
pip install $WORKSPACE


# unit tests
nosetests --with-xunit \
         --cover-package=opnfv \
         --with-coverage \
         --cover-xml \
         --cover-html \
         tests/unit
rc=$?

deactivate
