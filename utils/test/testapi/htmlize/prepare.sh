#!/bin/bash

# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# Install Pre-requisites
pip install requests

# Swgger Codegen Tool
url="http://repo1.maven.org/maven2/io/swagger/swagger-codegen-cli/2.2.1/swagger-codegen-cli-2.2.1.jar"

if [[ `wget -S --spider $url  2>&1 | grep 'HTTP/1.1 200 OK'` ]]; 
then 
	wget http://repo1.maven.org/maven2/io/swagger/swagger-codegen-cli/2.2.1/swagger-codegen-cli-2.2.1.jar -O swagger-codegen-cli.jar 
else
	echo "Swagger Codegen Jar File not found"
fi

# Start OPNFV Test API Server
cd ../
pip install -r requirements.txt
./install.sh
opnfv-testapi &
