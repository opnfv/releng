#!/bin/bash
set -e
set -o pipefail

project="$(git remote -v | head -n1 | awk '{{print $2}}' | sed -e 's,.*:\(.*/\)\?,,' -e 's/\.git$//')"
export PATH=$PATH:/usr/local/bin/

git_sha1="$(git rev-parse HEAD)"
res_build_date="$(date)"

dir_result="/home/jenkins-ci/functest/results"

# copy folder to artifact
echo "copy result files to artifact"
gsutil cp -r "$dir_result" gs://artifacts.opnfv.org/"$project"/
