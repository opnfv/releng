#!/bin/bash

usage="
Script to install dashboard automatically.
This script should be run under root.

usage:
    bash $(basename "$0") [-h|--help] [-t <test_name>]

where:
    -h|--help         show this help text
    -p|--project      project dashboard
      <project_name>"

# Parse parameters
while [[ $# > 0 ]]
    do
    key="$1"
    case $key in
        -h|--help)
            echo "$usage"
            exit 0
            shift
        ;;
        -p|--project)
            PROJECT="$2"
            shift
        ;;
        *)
            echo "unknown option $1 $2"
            exit 1
        ;;
    esac
    shift # past argument or value
done

if [[ $(whoami) != "root" ]]; then
    echo "Error: This script must be run as root!"
    exit 1
fi

if [ -z ${PROJECT+x} ]; then
    echo "project must be specified"
    exit 1
fi

if [ $PROJECT != "functest" ] && [ $PROJECT != "qtip" ];then
    echo "unsupported project $PROJECT"
    exit 1
fi

cp -f dashboard/$PROJECT/format.py dashboard/mongo2elastic
cp -f dashboard/$PROJECT/testcases.yaml etc/
python setup.py install
