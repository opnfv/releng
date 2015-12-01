#!/bin/bash
set +e
cd ~/joid/ci/

echo "------ Recover Juju environment to use MAAS ------"
cp $JOID_LOCAL_CONFIG_FOLDER/environment.yaml .
