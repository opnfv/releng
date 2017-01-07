#!/bin/bash
set -o errexit

echo "Running unit tests..."

# Creating virtual environment
virtualenv $WORKSPACE/testapi_venv
source $WORKSPACE/testapi_venv/bin/activate

cd $WORKSPACE/utils/test/testapi/

# Install requirements
pip install -r requirements.txt
pip install -r test-requirements.txt

# Run unit tests
bash run_test.sh
