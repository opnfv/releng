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
    gsutil cp -r build/design_docs "gs://$gs_path_branch/"
    gsutil cp -r build/requirements/html "gs://$gs_path_branch/"
    gsutil cp -r build/requirements/latex/*.pdf "gs://$gs_path_branch/"
    echo
    echo "Latest document is available at http://$gs_path_branch"

    if gsutil ls "gs://$gs_path_review" > /dev/null 2>&1 ; then
        echo
        echo "Deleting Out-of-dated Documents..."
        gsutil rm -r "gs://$gs_path_review"
    fi
fi
