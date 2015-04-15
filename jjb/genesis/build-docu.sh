#!/bin/bash
set -xv
for file in $(find . -type f -iname '*.rst'); do
        file_cut="${{file%.*}}"
        html_file=$file_cut".html"
        pdf_file=$file_cut".pdf"
        rst2html $file > $html_file
        rst2pdf $file -o $pdf_file
	gs_cp_folder=$(echo $file| cut -d "/" -f2,3)
	/usr/local/bin/gsutil cp $html_file gs://artifacts.opnfv.org/genesis/$gs_cp_folder/
	/usr/local/bin/gsutil cp $pdf_file gs://artifacts.opnfv.org/genesis/$gs_cp_folder/
done
