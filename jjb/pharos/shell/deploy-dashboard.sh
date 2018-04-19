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
cp $HOME/rsa.pub $WORKSPACE/dashboard
cp $HOME/rsa.pem $WORKSPACE/dashboard

cd $WORKSPACE/dashboard
docker-compose pull
docker-compose up -d
