#!/bin/bash
project="opnfvdocs"
export PATH=$PATH:/usr/local/bin/

files=()
while read -r -d ''; do
      files+=("$REPLY")
done < <(find . -type f -iname '*.rst' -print0)

for file in "${{files[@]}}"; do

  file_cut="${{file%.*}}"
  gs_cp_folder="${{file_cut#/}}"

    echo "rst2html $file"
    rst2html $file | gsutil cp -L gsoutput.txt - \
    gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder".html
    gsutil setmeta -h "Content-Type:text/html" \
                   -h "Cache-Control:private, max-age=0, no-transform" \
                   gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder".html
    cat gsoutput.txt

    echo "rst2pdf $file"
    rst2pdf "$file" -o - | gsutil cp -L gsoutput.txt - \
    gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder".html
    gsutil setmeta -h "Content-Type:application/pdf" \
                   -h "Cache-Control:private, max-age=0, no-transform" \
                   gs://artifacts.opnfv.org/"$project"/"$gs_cp_folder".pdf
    cat gsoutput.txt

done

rm -f gsoutput.txt
