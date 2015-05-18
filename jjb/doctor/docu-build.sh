#!/bin/bash
set -e
set -o pipefail

design_docs_dir="design_docs"
build_dir="build"
project="$(git remote -v | head -n1 | awk '{{print $2}}' | sed -e 's,.*:\(.*/\)\?,,' -e 's/\.git$//')"
export PATH=$PATH:/usr/local/bin/

make

# upload all built files
files=(
    $build_dir/$design_docs_dir
    $build_dir/requirements/html
    $build_dir/requirements/latex/*.pdf
)

for file in "${{files[@]}}"; do
    gsutil cp -r -L gsoutput.txt $file gs://artifacts.opnfv.org/$project/
    gsutil setmeta -h "Cache-Control:private, max-age=0, no-transform" \
	gs://artifacts.opnfv.org/$project/$file
    cat gsoutput.txt
    rm -f gsoutput.txt
done
