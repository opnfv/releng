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
TAR_FILE=pharos-dashboard-db-$DATE.tar.tz

mkdir -p $BACKUP_DIR
echo "-- $DATE --"
echo "--> Backing up Pharos Dashboard"

docker run --rm \
  -v pharos-data:/pharos-data:ro \
  -v $BACKUP_DIR:/backup \
  alpine \
  tar -czf /backup/$TAR_FILE -C /pharos-data ./

/usr/local/bin/gsutil cp $BACKUP_DIR/$TAR_FILE \
  gs://opnfv-backups/pharos-dashboard/ && rm $BACKUP_DIR/$TAR_FILE

echo "--> Pharos dashboard backup complete"
