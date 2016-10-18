#!/bin/bash

usage="
Script to install opnfv_tesgtapi automatically.
This script should be run under root.

usage:
    bash $(basename "$0") [-h|--help] [-t <test_name>]

where:
    -h|--help         show this help text"

if [[ $(whoami) != "root" ]]; then
    echo "Error: This script must be run as root!"
    exit 1
fi

cp -fr 3rd_party/static opnfv_testapi/tornado_swagger
python setup.py install
rm -fr opnfv_testapi/tornado_swagger/static
