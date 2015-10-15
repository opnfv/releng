#!/bin/bash
set -e
set -o pipefail

export PATH=$PATH:/usr/local/bin/
git_sha1="$(git rev-parse HEAD)"

clean() {{
if [[ -d docs/output ]]; then
rm -rf docs/output
echo "cleaning up output directory"
fi
}}

gerritcomment() {{
    echo "$gerrit_comment"
    ssh -p 29418 gerrit.opnfv.org gerrit review -p $GERRIT_PROJECT -m \
    "$gerrit_comment" $GERRIT_PATCHSET_REVISION
}}

trap clean EXIT TERM INT SIGTERM SIGHUP

#collect files
files=()
while read -r -d ''; do
  files+=("$REPLY")
done < <(find docs/ -type f -iname '*.rst' -print0)

#set sha1
for file in "${{files[@]}}"; do
  sed -i "s/_sha1_/$git_sha1/g" $file
done


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

done

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

for dir in "${{directories[@]}}"; do
  echo
  echo "#############################"
  echo "UPLOADING DOCS in ${{dir##*/}}"
  echo "#############################"
  echo


  if [[ $JOB_NAME =~ "verify" ]] ; then

    #upload artifacts for verify job
    gsutil cp -r docs/output/"${{dir##*/}}/" "gs://$gs_path_review/"

    # post link to gerrit as comment
    gerrit_comment="$(echo '"Document is available at 'http://$gs_path_review/"${{dir##*/}}"/index.html' for review"')"
    gerritcomment

    #set cache to 0
    for x in $(gsutil ls gs://$gs_path_review/"${{dir##*/}}" | grep html);
    do
      gsutil setmeta -h "Content-Type:text/html" \
      -h "Cache-Control:private, max-age=0, no-transform" \
      "$x"
    done

  else

    #upload artifacts for merge job
    gsutil cp -r docs/output/"${{dir##*/}}" "gs://$gs_path_branch/docs/"
    echo "Latest document is available at http://$gs_path_branch/docs/"${{dir##*/}}"/index.html"

    #set cache to 0
    for x in $(gsutil ls gs://$gs_path_branch/"${{dir}}" | grep html);
    do
      gsutil setmeta -h "Content-Type:text/html" \
      -h "Cache-Control:private, max-age=0, no-transform" \
      "$x"
    done

    #Clean up review when merging
    if gsutil ls "gs://$gs_path_review" > /dev/null 2>&1 ; then
      echo
      echo "Deleting Out-of-dated Documents..."
      gsutil rm -r "gs://$gs_path_review"
    fi

  fi

done

#check that line length is less than 120 characters
for file in "${{files[@]}}"; do
  toolong=""
  toolong+="$(awk 'length($0) > 120 {{ print NR ":" $0 }}' "$file")"
  if ! [[ -z "$toolong" ]];
  then
    echo "Build failed, please shorten the following lines to less than 120 characters"
    echo "$file"
    echo "$toolong"
    status=failed
    gerrit_comment="Build failed, please shorten the following lines to less than 120 characters
    "$file"
    "$toolong""
    gerritcomment

  fi
done

#check that there are no trailing white spaces
for file in "${{files[@]}}"; do
  blanks=""
  blanks+="$(grep -n '[[:space:]]$' "$file")"
  if ! [[ -z "$blanks" ]];
  then
    echo "Build failed, please remove the following trailing whitespace"
    echo "$file"
    echo "$blanks"
    status=failed
    gerrit_comment="Build failed, please the following trailing whitespace
    "$file"
    "$blanks""
    gerritcomment
  fi
done

if [[ $status == "failed" ]]; then exit 1; fi
