#!/bin/bash
cd $WORKSPACE
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
cmd="anteater --project $PROJECT"
echo "Executing command inside container"
echo "$cmd"
echo "--------------------------------------------------------"
docker exec $container_id $cmd > $WORKSPACE/securityaudit.log 2>&1
exit_code=$?
echo "--------------------------------------------------------"
echo "Stopping docker container with ID $container_id"
docker stop $container_id

cat securityaudit.log

gsutil cp $WORKSPACE/securityaudit.log \
    gs://$GS_URL/$PROJECT-securityaudit-weekly.log 2>&1

gsutil -m setmeta \
    -h "Content-Type:text/html" \
    -h "Cache-Control:private, max-age=0, no-transform" \
    gs://$GS_URL/$PROJECT-securityaudit-weekly.log > /dev/null 2>&1
