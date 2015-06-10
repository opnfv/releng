#!/bin/bash
set -e
set -o pipefail

project="$(git remote -v | head -n1 | awk '{{print $2}}' | sed -e 's,.*:\(.*/\)\?,,' -e 's/\.git$//')"
export PATH=$PATH:/usr/local/bin/

git_sha1="$(git rev-parse HEAD)"
docu_build_date="$(date)"

if [[ $GERRIT_EVENT_TYPE != "change-merged" ]] ; then
	if [[ $GERRIT_BRANCH != "master" ]] ; then
		gerrit_branch=`echo $GERRIT_BRANCH | cut -f2 -d"/"`
		gs_path="$project/$gerrit_branch"
	else
		gs_path="$project"
	fi
fi

files=()
while read -r -d ''; do
	files+=("$REPLY")
done < <(find * -type f -iname '*.rst' -print0)

for file in "${{files[@]}}"; do

	file_cut="${{file%.*}}"
	gs_cp_folder="${{file_cut}}"

	# sed part
	sed -i "s/_sha1_/$git_sha1/g" $file
	sed -i "s/_date_/$docu_build_date/g" $file

	# rst2html part
	echo "rst2html $file"
	rst2html $file | gsutil cp -L gsoutput.txt - \
	gs://artifacts.opnfv.org/"$gs_path"/"$gs_cp_folder".html
	gsutil setmeta -h "Content-Type:text/html" \
			-h "Cache-Control:private, max-age=0, no-transform" \
			gs://artifacts.opnfv.org/"$gs_path"/"$gs_cp_folder".html
	cat gsoutput.txt
	rm -f gsoutput.txt

	echo "rst2pdf $file"
	rst2pdf $file -o - | gsutil cp -L gsoutput.txt - \
	gs://artifacts.opnfv.org/"$gs_path"/"$gs_cp_folder".pdf
	gsutil setmeta -h "Content-Type:application/pdf" \
			-h "Cache-Control:private, max-age=0, no-transform" \
			gs://artifacts.opnfv.org/"$gs_path"/"$gs_cp_folder".pdf
	cat gsoutput.txt
	rm -f gsoutput.txt

done

images=()
while read -r -d ''; do
        images+=("$REPLY")
done < <(find * -type f \( -iname \*.jpg -o -iname \*.png \) -print0)

for img in "${{images[@]}}"; do

	# uploading found images
	echo "uploading $img"
        cat "$img" | gsutil cp -L gsoutput.txt - \
        gs://artifacts.opnfv.org/"$gs_path"/"$img"
        gsutil setmeta -h "Content-Type:image/jpeg" \
                        -h "Cache-Control:private, max-age=0, no-transform" \
                        gs://artifacts.opnfv.org/"$gs_path"/"$img"
        cat gsoutput.txt
        rm -f gsoutput.txt

done
