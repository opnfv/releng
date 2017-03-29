#!/bin/bash
##############################################################################
# Copyright (c) 2016 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

BASEDIR=`dirname $0`

#clean up correlated dockers and their images
bash ${BASEDIR}/docker_cleanup.sh -d bottlenecks --debug
bash ${BASEDIR}/docker_cleanup.sh -d yardstick --debug
bash ${BASEDIR}/docker_cleanup.sh -d kibana --debug
bash ${BASEDIR}/docker_cleanup.sh -d elasticsearch --debug
bash ${BASEDIR}/docker_cleanup.sh -d influxdb --debug