#!/bin/bash

cd $WORKSPACE
if [ ! -d "$WORKSPACE/allrepos" ]; then
  mkdir $WORKSPACE/allrepos
fi

echo "--------------------------------------------------------"
vols="-v $WORKSPACE/allrepos/:/home/opnfv/anteater/allrepos/"
echo "Pulling releng-anteater docker image"
echo "--------------------------------------------------------"
docker pull opnfv/releng-anteater
echo "--------------------------------------------------------"
cmd="sudo docker run --privileged=true -id $vols opnfv/releng-anteater /bin/bash"
echo "Running docker command $cmd"
container_id=$($cmd)
echo "Container ID is $container_id"
source $WORKSPACE/opnfv-projects.sh
for project in "${PROJECT_LIST[@]}"

do
  cmd="anteater --project testproj --path /home/opnfv/anteater/allrepos/$project"
  echo "Executing command inside container"
  echo "$cmd"
  echo "--------------------------------------------------------"
  docker exec $container_id $cmd > $WORKSPACE/"$project".securityaudit.log 2>&1
done

exit_code=$?
echo "--------------------------------------------------------"
echo "Stopping docker container with ID $container_id"
docker stop $container_id


#gsutil cp $WORKSPACE/securityaudit.log \
#    gs://$GS_URL/$PROJECT-securityaudit-weekly.log 2>&1
#
#gsutil -m setmeta \
#    -h "Content-Type:text/html" \
#    -h "Cache-Control:private, max-age=0, no-transform" \
#    gs://$GS_URL/$PROJECT-securityaudit-weekly.log > /dev/null 2>&1
