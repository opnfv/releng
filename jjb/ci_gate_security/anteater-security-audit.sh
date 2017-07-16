#!/bin/bash
cd $WORKSPACE
REPORTDIR='.reports'
mkdir -p $REPORTDIR
echo "Generating patchset file to list changed files"
git diff HEAD^1 --name-only | sed "s#^#/home/opnfv/anteater/$PROJECT/#" > $WORKSPACE/patchset
echo "Changed files are"
echo "--------------------------------------------------------"
cat $WORKSPACE/patchset
echo "--------------------------------------------------------"

vols="-v $WORKSPACE:/home/opnfv/anteater/$PROJECT -v $WORKSPACE/$REPORTDIR:/home/opnfv/anteater/$REPORTDIR"
envs="-e PROJECT=$PROJECT"

echo "Pulling releng-anteater docker image"
echo "--------------------------------------------------------"
docker pull opnfv/releng-anteater
echo "--------------------------------------------------------"

cmd="docker run -i $envs $vols --rm opnfv/releng-anteater \
/home/opnfv/venv/bin/anteater --project $PROJECT --patchset /home/opnfv/anteater/$PROJECT/patchset"
echo "Running docker container"
echo "$cmd"
$cmd > $WORKSPACE/securityaudit.log 2>&1
exit_code=$?
echo "--------------------------------------------------------"
echo "Docker container exited with code: $exit_code"
echo "--------------------------------------------------------"
cat securityaudit.log
exit 0
