#!/bin/bash
set -o errexit
set -o pipefail

# ******************************
# prepare the env for the tests
# ******************************
# Either Workspace is set (CI)
if [ -z $WORKSPACE ]
then
    WORKSPACE="."
fi

export CONFIG_REPORTING_YAML=./reporting.yaml

# ***************
# Run unit tests
# ***************
echo "Running unit tests..."

# start vitual env
virtualenv $WORKSPACE/reporting_venv
source $WORKSPACE/reporting_venv/bin/activate

# install python packages
easy_install -U setuptools
easy_install -U pip
pip install -r $WORKSPACE/docker/requirements.pip
pip install -e $WORKSPACE

python $WORKSPACE/setup.py develop

# unit tests
# TODO: remove cover-erase
# To be deleted when all functest packages will be listed
nosetests --with-xunit \
         --cover-package=utils \
         --with-coverage \
         --cover-xml \
         tests/unit
rc=$?

deactivate
