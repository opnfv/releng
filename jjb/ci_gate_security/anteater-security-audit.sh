#!/bin/bash
cd $WORKSPACE
echo "Generating patchset file to list changed files"
git diff HEAD^1 --name-only | sed "s#^#/home/opnfv/anteater/$PROJECT/#" > $WORKSPACE/patchset
echo "Changed files are"
echo "--------------------------------------------------------"
cat $WORKSPACE/patchset
echo "--------------------------------------------------------"

vols="-v $WORKSPACE:/home/opnfv/anteater/$PROJECT"
envs="-e PROJECT=$PROJECT"

echo "Pulling releng-anteater docker image"
echo "--------------------------------------------------------"
docker pull opnfv/releng-anteater
echo "--------------------------------------------------------"

cmd="sudo docker run --privileged=true -id $envs $vols opnfv/releng-anteater /bin/bash"
echo "Running docker command $cmd"
container_id=$($cmd)
echo "Container ID is $container_id"
cmd="anteater --project $PROJECT --patchset /home/opnfv/anteater/$PROJECT/patchset"
echo "Executing command inside container"
echo "$cmd"
echo "--------------------------------------------------------"
docker exec $container_id $cmd > $WORKSPACE/securityaudit.log 2>&1
exit_code=$?
echo "--------------------------------------------------------"
echo "Stopping docker container with ID $container_id"
docker stop $container_id
exit 0
