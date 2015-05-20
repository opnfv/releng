#!/bin/bash
# 150519.1
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

for file in "${{files[@]}}"; do

        file_cut="${{file%.*}}"
        gs_cp_folder="${{file_cut}}"

        # sed part
        sed -i "s/1df1742ff3ca67b89ce33590cd1a5b96408073af/$git_sha1/g" $file
        sed -i "s/Wed May 13 17:45:03 UTC 2015/$docu_build_date/g" $file

        # rst2html part
        echo "rst2html $file"
        rst2html $file > $file_cut".html"

        echo "rst2pdf $file"
        rst2pdf $file -o $file_cut".pdf"

done

#the double {{ in file_cut="${{file%.*}}" is to escape jjb's yaml