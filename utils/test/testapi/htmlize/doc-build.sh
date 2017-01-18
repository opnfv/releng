#!/bin/bash

set -o errexit

# Create virtual environment
source $WORKSPACE/testapi_venv/bin/activate

# Install Pre-requistics
pip install requests

python ./utils/test/testapi/htmlize/htmlize.py -o ${WORKSPACE}/
