#!/bin/bash

#
# Author: Serena Feng (feng.xiaoewi@zte.com.cn)
# Update testapi on remote server using ansible playbook automatically
#
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
#

set -e

usage="Script to trigger update automatically.

usage:
    bash $(basename "$0") [-h|--help] [-h <host>] [-u username] [-i identityfile] [-e|--execute]

where:
    -h|--help           show this help text
    -r|--remote         remote server
    -u|--user           ssh username used to access to remote server
    -i|--identity       ssh PublicKey file used to access to remote server
    -e|--execute        execute update, if not set just check the ansible connectivity"

remote=testresults.opnfv.org
user=root
identity=~/.ssh/id_rsa
hosts=./hosts
execute=false

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
        -r|--remote)
            remote="$2"
            shift
        ;;
        -u|--user)
            user="$2"
            shift
        ;;
        -i|--identity)
            identity="$2"
            shift
        ;;
        -e|--execute)
            execute=true
        ;;
        *)
            echo "unknown option"
            exit 1
        ;;
    esac
    shift # past argument or value
done

echo $remote > $hosts

echo "add authentication"
ssh-add $identity

echo "test ansible connectivity"
ansible -i ./hosts $remote -m ping -u $user

echo "test playbook connectivity"
ansible-playbook -i $hosts test.yml -e "host=$remote user=$user"

if [ $execute == true ]; then
    echo "do update"
    ansible-playbook -i $hosts update.yml -e "host=$remote \
    user=$user \
    port=8082 \
    image=opnfv/testapi \
    update_path=/home/$user/testapi \
    mongodb_url=mongodb://172.17.0.1:27017 \
    swagger_url=http://testresults.opnfv.org/test"
fi

rm -fr $hosts
ssh-agent -k
