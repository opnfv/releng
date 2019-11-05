#!/bin/bash -eux
##############################################################################
# Copyright (c) 2018 Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

BACKUP_DIR=$HOME/backups
DATE=$(date +%Y%m%d)
TAR_FILE=laas-dashboard-db-$DATE.tar.tz

mkdir -p $BACKUP_DIR
echo "-- $DATE --"
echo "--> Backing up Lab as a Service Dashboard"

docker run --rm \
  -v laas-data:/laas-data:ro \
  -v $BACKUP_DIR:/backup \
  alpine \
  tar -czf /backup/$TAR_FILE -C /laas-data ./

/usr/local/bin/gsutil cp $BACKUP_DIR/$TAR_FILE \
  gs://opnfv-backups/laas-dashboard/ && rm $BACKUP_DIR/$TAR_FILE

echo "--> LAAS dashboard backup complete"
