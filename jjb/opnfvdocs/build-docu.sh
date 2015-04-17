#!/bin/bash
#set -xv
echo "Hello world!"
#project="opnfvdocs"
#export PATH=$PATH:/usr/local/bin/
#
#files=()
#while read -r -d ''; do
#      files+=("$REPLY")
#done < <(find . -type f -iname '*.rst' -print0)
# for loop to parse files
#for file in "${{files[@]}}"; do
#	file_cut="${{file%.*}}"
#	gs_cp_folder=$(dirname "${file}")
#	# html files handle
#	html_file=$file_cut".html"
#		echo "rst2html $file"
#		rst2html $file | gsutil cp -L gsoutput.txt - \
#			gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder"/$(basename "$html_file")
#			gsutil setmeta -h "Content-Type:text/html" \
#					-h "Cache-Control:private, max-age=0, no-transform" \
#			gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder"/$(basename "$html_file")
#	cat gsoutput.txt
#
#	# pdf files handle
#	pdf_file="$file_cut"".pdf"
#		echo "rst2pdf $file"
#		rst2pdf "$file" -o - | gsutil cp -L gsoutput.txt - \
#			gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder"/$(basename "$pdf_file")
#			gsutil setmeta -h "Content-Type:text/html" \
#					-h "Cache-Control:private, max-age=0, no-transform" \
#			gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder"/$(basename "$pdf_file")
#	cat gsoutput.txt
#done
##removing the temp file
#rm -f gsoutput.txt
