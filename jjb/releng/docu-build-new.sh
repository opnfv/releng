#!/bin/bash 
set -e
set -o pipefail

export PATH=$PATH:/usr/local/bin/

clean() {{
if [[ -d docs/output ]]; then
rm -rf docs/output
echo "cleaning up output directory"
fi
}} 

trap clean EXIT TERM INT SIGTERM SIGHUP

directories=()
while read -d $'\n'; do
        directories+=("$REPLY")
done < <(find docs/ -name 'index.rst' -printf '%h\n' | sort -u )

for dir in "${{directories[@]}}"; do
echo
echo "#############################"
echo "Building DOCS in ${{dir##*/}}"
echo "#############################"
echo

if [[ ! -d docs/output/"${{dir##*/}}/" ]]; then
  mkdir -p docs/output/"${{dir##*/}}/"
fi

sphinx-build -b html -E -c docs/etc/ ""$dir"/" docs/output/"${{dir##*/}}/"

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
    gsutil cp -r docs/output/"${{dir##*/}}/" "gs://$gs_path_review/"
    echo
    # post link to gerrit as comment
    gerrit_comment=$(echo '"Document is available at 'http://$gs_path_review/"${{dir##*/}}"/index.html' for review"')
    echo "$gerrit_comment"
    ssh -p 29418 gerrit.opnfv.org gerrit review -p $GERRIT_PROJECT -m \
    $gerrit_comment $GERRIT_PATCHSET_REVISION
else
    gsutil cp -r docs/output/"${{dir##*/}}/" "gs://$gs_path_branch/design_docs/"

    echo "Latest document is available at http://$gs_path_branch/design_docs/index.html"

    if gsutil ls "gs://$gs_path_review" > /dev/null 2>&1 ; then
        echo
        echo "Deleting Out-of-dated Documents..."
        gsutil rm -r "gs://$gs_path_review"
    fi
fi


done
