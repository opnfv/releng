#!/bin/bash

set -e
set -o pipefail

export PATH=$PATH:/usr/local/bin/


directories=()
while read -d $'\n'; do
  directories+=("$REPLY")
done < <(find docs/ -name 'index.rst' -printf '%h\n' | sort -u )

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

echo
echo "#############################"
echo "UPLOADING DOCS in ${{dir##*/}}"
echo "#############################"
echo

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
