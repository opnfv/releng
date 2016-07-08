#!/bin/bash

echo "launch Moon unit tests"

sudo apt-get install -y git python-nose

cd /tmp
git clone https://git.opnfv.org/moon

nosetest /tmp/moon/keystone-moon/keystone/tests/moon/unit

rm -rf /tmp/moon