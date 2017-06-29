#!/bin/bash
set -o errexit
set -o pipefail


# Get script directory
SCRIPTDIR=`dirname $0`

# Creating virtual environment
if [ ! -z $VIRTUAL_ENV ]; then
    venv=$VIRTUAL_ENV
else
    venv=$SCRIPTDIR/.venv
    virtualenv $venv
fi

source $venv/bin/activate

export CONFIG_REPORTING_YAML=$SCRIPTDIR/reporting.yaml

# ***************
# Run unit tests
# ***************
echo "Running unit tests..."

# install python packages
easy_install -U setuptools
easy_install -U pip
pip install -r $SCRIPTDIR/docker/requirements.pip
pip install -e $SCRIPTDIR

python $SCRIPTDIR/setup.py develop

# unit tests
# TODO: remove cover-erase
# To be deleted when all functest packages will be listed
nosetests --with-xunit \
         --cover-package=$SCRIPTDIR/utils \
         --with-coverage \
         --cover-xml \
         $SCRIPTDIR/tests/unit
rc=$?

deactivate
