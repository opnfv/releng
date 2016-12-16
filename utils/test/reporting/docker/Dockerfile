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
LABEL version="danube.1.0" description="OPNFV Test Reporting Docker container"

ARG BRANCH=master

ENV HOME /home/opnfv
ENV working_dir /home/opnfv/utils/test/reporting
ENV TERM xterm
ENV COLORTERM gnome-terminal
ENV CONFIG_REPORTING_YAML /home/opnfv/utils/test/reporting/reporting.yaml

# Packaged dependencies
RUN apt-get update && apt-get install -y \
ssh \
python-pip \
git-core \
wkhtmltopdf \
--no-install-recommends

RUN pip install --upgrade pip

RUN git clone --depth 1 https://gerrit.opnfv.org/gerrit/releng /home/opnfv
RUN pip install -r ${working_dir}/docker/requirements.pip

WORKDIR ${working_dir}
RUN docker/reporting.sh
