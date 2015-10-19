#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Starting the push of Functest Docker image."
echo "--------------------------------------------------------"
echo

# List the images
docker images

# Push to the Dockerhub repository
docker push opnfv/functest