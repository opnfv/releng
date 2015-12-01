#!/bin/bash
set +e
cd ~/joid/ci

echo "------ Backup Juju environment ------"
cp environment.yaml $JOID_LOCAL_CONFIG_FOLDER

echo "------ Clean MAAS and Juju ------"
./clean.sh
