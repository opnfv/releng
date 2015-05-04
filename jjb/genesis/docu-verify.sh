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
done < <(find . -type f -iname '*.rst' -print0)

for file in "${{files[@]}}"; do

	file_cut="${{file%.*}}"
	gs_cp_folder="$(echo "$file"| cut -d "/" -f2,3)"

	# sed part
	sed -i "s/_sha1_/$git_sha1/g" $file
	sed -i "s/_date_/$docu_build_date/g" $file

	# rst2html part
	echo "rst2html $file"
	rst2html $file > $file_cut".html"

	echo "rst2pdf $file"
	rst2pdf $file -o $file_cut".pdf"

done

