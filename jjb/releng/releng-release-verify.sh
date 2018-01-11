#!/bin/bash
set -x

# Activate virtualenv, supressing shellcheck warning
# shellcheck source=/dev/null
. $WORKSPACE/venv/bin/activate
pip install -r releases/scripts/requirements.txt

STREAM=${STREAM:-'nostream'}
RELEASE_FILES=$(git diff HEAD^1 --name-only | grep "^releases/$STREAM")

for release_file in $RELEASE_FILES; do
    python releases/scripts/verify_schema.py \
    -s releases/schema.yaml \
    -y $release_file
done
