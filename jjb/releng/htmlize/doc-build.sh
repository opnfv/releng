#!/bin/bash

set -o errexit

# Create virtual environment
virtualenv $WORKSPACE/testapi_venv
source $WORKSPACE/testapi_venv/bin/activate

# Swgger Codegen Tool
url="http://repo1.maven.org/maven2/io/swagger/swagger-codegen-cli/2.2.1/swagger-codegen-cli-2.2.1.jar"

# Check for jar file locally and in the repo
if [ ! -f swagger-codegen-cli.jar ];
then
    wget http://repo1.maven.org/maven2/io/swagger/swagger-codegen-cli/2.2.1/swagger-codegen-cli-2.2.1.jar -O swagger-codegen-cli.jar
fi

# Install Pre-requistics
pip install requests

python ./utils/test/testapi/htmlize/htmlize.py -o ${WORKSPACE}/
