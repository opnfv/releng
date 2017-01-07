#!/bin/bash

# Create virtual environment
source $WORKSPACE/testapi_venv/bin/activate

python ./utils/test/testapi/htmlize/htmlize.py -o ${WORKSPACE}/
