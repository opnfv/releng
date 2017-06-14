#!/bin/bash

#WORKSPACE=/tmp/test/

cd $WORKSPACE
mkdir $WORKSPACE/allrepos
cd $WORKSPACE/allrepos

#Clone all repos for scan
for x in $(ssh gerrit.opnfv.org -p 29418 'gerrit ls-projects');
do git clone ssh://gerrit.opnfv.org:29418/$x
done


#Set docker mounts
echo "--------------------------------------------------------"
vols="-v $WORKSPACE/allrepos/:/home/opnfv/anteater/allrepos/"
echo "Pulling releng-anteater docker image"
echo "--------------------------------------------------------"
docker pull opnfv/releng-anteater
echo "--------------------------------------------------------"

#Starts a shell inside docker
cmd="docker run --privileged=true -id $vols opnfv/releng-anteater /bin/bash"
echo "Running docker command $cmd"
container_id=$($cmd)
echo "Container ID is $container_id"


for project in $(ssh gerrit.opnfv.org -p 29418 'gerrit ls-projects');
do
        cmd="anteater --project testproj --path /home/opnfv/anteater/allrepos/$project"
        echo "Executing command inside container"
        echo "$cmd"
        echo "--------------------------------------------------------"
        docker exec $container_id $cmd
done


exit_code=$?


echo "--------------------------------------------------------"
echo "Stopping docker container with ID $container_id"
docker stop $container_id

#TODO get reports
# /home/opnfv/reports/*-$project.log
# copy to gce (ls on host at least)
#
#gsutil cp $WORKSPACE/securityaudit.log \
#    gs://$GS_URL/$PROJECT-securityaudit-weekly.log 2>&1
#
#gsutil -m setmeta \
#    -h "Content-Type:text/html" \
#    -h "Cache-Control:private, max-age=0, no-transform" \
#    gs://$GS_URL/$PROJECT-securityaudit-weekly.log > /dev/null 2>&1
