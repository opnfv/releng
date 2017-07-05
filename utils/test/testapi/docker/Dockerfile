#######################################################
#   Docker container for OPNFV-TESTAPI
#######################################################
# Purpose: run opnfv-testapi for gathering test results
#
# Maintained by SerenaFeng
# Build:
#    $ docker build -t opnfv/testapi:tag .
#
# Execution:
#    $ docker run -dti -p 8001:8000 \
#      -e "base_url=http://10.63.243.17:8001" \
#      -e "mongodb_url=mongodb://10.63.243.17:27017/" \
#      opnfv/testapi:tag
#
# NOTE: providing swagger_url, mongodb_url is optional.
#       If not provided, it will use the default one
#       configured in config.ini
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#

FROM ubuntu:14.04
MAINTAINER SerenaFeng <feng.xiaowei@zte.com.cn>
LABEL version="v1" description="OPNFV TestAPI Docker container"

ENV HOME /home

# Packaged dependencies
RUN apt-get update && apt-get install -y \
curl \
git \
gcc \
wget \
python-dev \
python-pip \
crudini \
--no-install-recommends

RUN pip install --upgrade pip

RUN git config --global http.sslVerify false
RUN git clone https://gerrit.opnfv.org/gerrit/releng /home/releng

WORKDIR /home/releng/utils/test/testapi/
RUN pip install -r requirements.txt
RUN bash install.sh
CMD ["bash", "docker/start-server.sh"]
