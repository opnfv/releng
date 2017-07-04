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
ENV http_proxy http://proxy.rd.francetelecom.fr:8080/
ENV https_proxy https://proxy.rd.francetelecom.fr:8080/

WORKDIR ${HOME}
# Packaged dependencies
RUN apt-get update && apt-get install -y \
ssh \
python-pip \
git-core \
nodejs \
npm \
supervisor \
--no-install-recommends

RUN pip install --upgrade pip

RUN git clone --depth 1 https://gerrit.opnfv.org/gerrit/releng ${HOME}/releng
RUN pip install -r ${working_dir}/requirements.txt

WORKDIR ${working_dir}
RUN python setup.py install
RUN docker/reporting.sh
RUN docker/web_server.sh

expose 8000

CMD ["/usr/bin/supervisord"]
