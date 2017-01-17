#!/bin/bash

# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

#Creating virtual environment
virtualenv testapi_venv
source testapi_venv/bin/activate

# Swgger Codegen Tool
url="http://repo1.maven.org/maven2/io/swagger/swagger-codegen-cli/2.2.1/swagger-codegen-cli-2.2.1.jar"

#Check for jar file locally and in the repo
if [ ! -f swagger-codegen-cli.jar ];
then
    wget http://repo1.maven.org/maven2/io/swagger/swagger-codegen-cli/2.2.1/swagger-codegen-cli-2.2.1.jar -O swagger-codegen-cli.jar
fi

# Start OPNFV Test API Server
cd utils/test/testapi/
pip install -r requirements.txt
./install.sh
opnfv-testapi -c ../../../testapi_venv/etc/opnfv_testapi/config.ini &
