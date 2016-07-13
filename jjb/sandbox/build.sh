#!/bin/bash
#set -o errexit
#set -o nounset
#set -o pipefail

# get the job type
# we only support verify, merge, daily and weekly jobs
if [[ "$JOB_NAME" =~ (verify|merge|daily|weekly) ]]; then
    JOB_TYPE=${BASH_REMATCH[0]}
else
    echo "Unable to determine job type!"
    exit 1
fi

# do stuff differently based on the job type
case "$JOB_TYPE" in
    verify)
        echo "Running as part of verify job"
        ;;
    merge)
        echo "Running as part of merge job"
        ;;
    daily)
        echo "Running as part of daily job"
        ;;
    weekly)
        echo "Running as part of weekly job"
        ;;
    *)
        echo "Job type $JOB_TYPE is not supported!"
        exit 1
esac

# this just shows we can get the patch/commit information
# no matter what job we are executed by
cd $WORKSPACE
echo
echo "Commit Message is"
echo "-------------------------------------"
git log --format=%B -n 1 $(git rev-parse HEAD)
echo "-------------------------------------"
echo
echo "Repo contents"
echo "-------------------------------------"
ls -al
echo "-------------------------------------"
echo
echo "Changed files are"
echo "-------------------------------------"
git diff origin/master --name-only
echo "-------------------------------------"
echo
echo "Change introduced"
echo "-------------------------------------"
git diff origin/master
echo "-------------------------------------"
echo
echo "git show"
echo "-------------------------------------"
git show
echo "-------------------------------------"

sleep 60
