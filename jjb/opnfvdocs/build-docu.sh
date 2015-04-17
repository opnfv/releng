#!/bin/bash
set -xv
project="opnfvdocs"
#export PATH=$PATH:/usr/local/bin/

files=()
while read -r -d ''; do
      files+=("$REPLY")
done < <(find . -type f -iname '*.rst' -print0)

for file in "${{files[@]}}"; do
	file_cut="${{file%.*}}"
	gs_cp_folder=$(dirname "${file}")

	html_file=$file_cut".html"
		echo "rst2html $file"
		rst2html $file | gsutil cp -L gsoutput.txt - \
    		gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder"/$(basename "$html_file")
		# The 3 lines below are used just to set medatada in order to reduce cache age to 0
    		gsutil setmeta -h "Content-Type:text/html" \
				-h "Cache-Control:private, max-age=0, no-transform" \
                     	       gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder"/$(basename "$html_file")
	cat gsoutput.txt

	pdf_file="$file_cut"".pdf"

	        echo "rst2pdf $file"
		rst2pdf "$file" -o - | gsutil cp -L gsoutput.txt - \
		gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder"/$(basename "$pdf_file")
                # The 3 lines below are used just to set medatada in order to reduce cache age to 0
		gsutil setmeta -h "Content-Type:application/pdf" \
	        		-h "Cache-Control:private, max-age=0, no-transform" \
		gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder"/$(basename "$pdf_file")
	cat gsoutput.txt

done

rm -f gsoutput.txt
