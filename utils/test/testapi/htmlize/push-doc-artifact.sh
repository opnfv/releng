#!/bin/bash

set -e
set -o pipefail

export PATH=$PATH:/usr/local/bin/

project=$PROJECT
workspace=$WORKSPACE
artifact_dir="functest/docs"

set +e
gsutil&>/dev/null
if [ $? != 0 ]; then
    echo "Not possible to push results to artifact: gsutil not installed"
else
    gsutil ls gs://artifacts.opnfv.org/"$project"/ &>/dev/null
    if [ $? != 0 ]; then
        echo "Not possible to push results to artifact: gsutil not installed."
    else
        echo "Uploading document to artifact $artifact_dir"
        gsutil cp "$workspace"/index.html gs://artifacts.opnfv.org/"$artifact_dir"/testapi.html >/dev/null 2>&1
        echo "Document can be found at http://artifacts.opnfv.org/functest/docs/testapi.html"
    fi
fi
