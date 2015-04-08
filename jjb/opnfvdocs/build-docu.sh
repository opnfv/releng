#!/bin/bash
for file in `find . -type f -iname '*.rst' `; do
	file_cut=`echo ${file%.*}`
        html_file=$file_cut".html"
        pdf_file=$file_cut".pdf"
        rst2html $file > $html_file
        rst2pdf $file -o $pdf_file ;
        sleep 1
done
