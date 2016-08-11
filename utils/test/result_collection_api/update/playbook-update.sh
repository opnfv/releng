#! /bin/bash

set -e

host=$1
user=$2
identity=$3

echo $1 > ./hosts

echo "add authentication"
ssh-add $identity

echo "test ansible connectivity"
ansible -i hosts $host -m ping -u $user

echo "test playbook connectivity"
ansible-playbook -i hosts test.yml -e "host=$host user=$user"

echo "do update"
ansible-playbook -i hosts update.yml -e "host=$host \
user=$user \
port=8082 \
image=opnfv/testapi \
update_path=/home/$user/testapi \
mongodb_url=mongodb://172.17.0.1:27017 \
swagger_url=http://testresults.opnfv.org/test"

ssh-agent -k

rm -fr ./hosts

