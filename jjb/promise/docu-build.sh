#!/bin/bash
set -e
set -o pipefail

export PATH=$PATH:/usr/local/bin/

echo
echo "Build"
echo "-----"
echo

make

echo
echo "Upload"
echo "------"
echo

# NOTE: make sure source parameters for GS paths are not empty.
[[ $GERRIT_CHANGE_NUMBER =~ .+ ]]
[[ $GERRIT_PROJECT =~ .+ ]]
[[ $GERRIT_BRANCH =~ .+ ]]

gs_path_review="artifacts.opnfv.org/review/$GERRIT_CHANGE_NUMBER"
if [[ $GERRIT_BRANCH = "master" ]] ; then
    gs_path_branch="artifacts.opnfv.org/$GERRIT_PROJECT"
else
    gs_path_branch="artifacts.opnfv.org/$GERRIT_PROJECT/${{GERRIT_BRANCH##*/}}"
fi

if [[ $JOB_NAME =~ "verify" ]] ; then
    gsutil cp -r build/* "gs://$gs_path_review/"
    echo
    echo "Document is available at http://$gs_path_review"
else
    gsutil cp -r build/requirements/latex/*.pdf "gs://$gs_path_branch/"
    echo
    echo "Document is available at http://$gs_path_branch"
fi

if [[ $GERRIT_EVENT_TYPE = "change-merged" ]] ; then
    echo
    echo "Clean Out-of-dated Documents"
    echo "----------------------------"
    echo
    gsutil rm -r "gs://$gs_path_review" || true
fi
