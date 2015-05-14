#!/bin/bash
set -e
set -o pipefail

design_docs_dir="design_docs"
build_dir="build"
project="$(git remote -v | head -n1 | awk '{{print $2}}' | sed -e 's,.*:\(.*/\)\?,,' -e 's/\.git$//')"
export PATH=$PATH:/usr/local/bin/

# build requirement HTML file
sphinx-build -b html -d "$build_dir"/requirements/doctrees requirements \
    "$build_dir"/requirements/html

# build requirement PDF file
sphinx-build -b latex -d "$build_dir"/requirements/doctrees requirements \
    "$build_dir"/requirements/latex
make -C "$build_dir"/requirements/latex all-pdf


# build design docs
files=()
while read -r -d ''; do
    files+=("$REPLY")
done < <(find * -type f -wholename $design_docs_dir/'*.rst' -print0)

mkdir -p "$build_dir"/"$design_docs_dir"
for file in "${{files[@]}}"; do

    file_cut="${{file%.*}}"

    # rst2html part
    echo "rst2html $file"
    rst2html --halt=2 "$file" "$build_dir"/"$file_cut".html

done
