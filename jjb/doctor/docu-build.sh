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

gs_path_change="artifacts.opnfv.org/$GERRIT_PROJECT/$GERRIT_CHANGE_NUMBER"
gs_path_branch="artifacts.opnfv.org/$GERRIT_PROJECT/$GERRIT_BRANCH"

if [[ $GERRIT_EVENT_TYPE = "change-merged" ]] ; then
    gsutil cp -r build/* "gs://$gs_path_change/"
    echo
    echo "Document is available at http://$gs_path_change"
else
    gsutil cp -r build/design_docs "gs://$gs_path_branch/"
    gsutil cp -r build/html "gs://$gs_path_branch/"
    gsutil cp -r build/latex/*.pdf "gs://$gs_path_branch/"
    echo
    echo "Document is available at http://$gs_path_branch"
fi

if [[ $GERRIT_EVENT_TYPE = "change-merged" ]] ; then
    echo
    echo "Clean Out-of-dated Documents"
    echo "----------------------------"
    echo
    gsutil rm -r "gs://$gs_path_change" || :
fi
