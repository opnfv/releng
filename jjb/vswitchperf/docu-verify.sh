#!/bin/bash
set -e
set -o pipefail

project="$(git remote -v | head -n1 | awk '{{print $2}}' | sed -e 's,.*:\(.*/\)\?,,' -e 's/\.git$//')"
export PATH=$PATH:/usr/local/bin/

git_sha1="$(git rev-parse HEAD)"
docu_build_date="$(date)"

files=()
while read -r -d ''; do
        files+=("$REPLY")
done < <(find * -type f -iname '*.rst' -print0)

for file in "${files[@]}"; do

        file_cut="${file%.*}"
        gs_cp_folder="${file_cut}"

        # sed part
        # add one '_' at the end of each trigger variable; ex: _sha1 +'_' & _date + '_' on both of the lines below
        # they were added here without the '_'suffix to avoid sed replacement
        sed -i "s/_sha1/$git_sha1/g" $file
        sed -i "s/_date/$docu_build_date/g" $file

        # rst2html part
        echo "rst2html $file"
        rst2html --exit-status=2 $file > $file_cut".html"

        echo "rst2pdf $file"
        rst2pdf $file -o $file_cut".pdf"

done

#the double {{ in file_cut="${{file%.*}}" is to escape jjb's yaml
