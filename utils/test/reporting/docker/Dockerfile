########################################
#   Docker container for OPNFV-REPORTING
########################################
# Purpose: run opnfv-reporting to provide consistent Testing reporting
#
# Maintained by Morgan Richomme
# Build:
#    $ docker build -t opnfv/testreporting:tag .
##
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#

FROM nginx:stable

MAINTAINER Morgan Richomme <morgan.richomme@orange.com>
LABEL version="1.0" description="OPNFV Test Reporting Docker container"

ARG BRANCH=master

ENV HOME /home/opnfv
ENV working_dir ${HOME}/releng/utils/test/reporting
ENV CONFIG_REPORTING_YAML ${working_dir}/reporting.yaml

WORKDIR ${HOME}
# Packaged dependencies
RUN apt-get update && apt-get install -y \
build-essential \
ssh \
curl \
gnupg \
python-pip \
python-dev \
python-setuptools \
git-core \
supervisor \
--no-install-recommends

RUN pip install --upgrade pip && easy_install -U setuptools==30.0.0

RUN git clone --depth 1 https://gerrit.opnfv.org/gerrit/releng /home/opnfv/releng
RUN pip install -r ${working_dir}/requirements.txt

RUN sh -c 'curl -sL https://deb.nodesource.com/setup_8.x | bash -' \
    && apt-get install -y nodejs \
    && npm install -g bower \
    && npm install -g grunt \
    && npm install -g grunt-cli

WORKDIR ${working_dir}
RUN python setup.py install
RUN docker/reporting.sh
RUN docker/web_server.sh

expose 8000

CMD ["/usr/bin/supervisord"]
