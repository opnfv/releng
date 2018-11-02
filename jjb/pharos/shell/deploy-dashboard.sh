#!/bin/bash -eux
##############################################################################
# Copyright (c) 2018 Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
cp $HOME/config.env $WORKSPACE/dashboard
cd $WORKSPACE/dashboard

docker-compose pull
docker-compose up -d

# Copy JIRA keys into web container
WEB_CONTAINER="$(docker ps --filter 'name=dg01' -q)"
docker cp $HOME/rsa.pub $WEB_CONTAINER:/pharos_dashboard/account/
docker cp $HOME/rsa.pem $WEB_CONTAINER:/pharos_dashboard/account/
