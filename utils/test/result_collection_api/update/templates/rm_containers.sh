#!/bin/bash

number=`docker ps -a | awk 'NR != 1' | grep testapi | wc -l`
if [ $number -gt 0 ]; then
    docker ps -a | awk 'NR != 1' | grep testapi | awk '{print $1}' | xargs docker rm -f &>/dev/null
fi
