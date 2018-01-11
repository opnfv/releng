#!/bin/bash
set -x

# Activate virtualenv, supressing shellcheck warning
# shellcheck source=/dev/null
. $WORKSPACE/venv/bin/activate

pip install -r releases/scripts/requirements.txt

STREAM=${STREAM:-'nostream'}
RELEASE_FILES=$(git diff HEAD^1 --name-only | grep "^releases/$STREAM")

for release_file in $RELEASE_FILES; do
    python releases/scripts/create_branch.py -f $release_file # && \
    python releases/scripts/create_jobs.py -f $release_file
done
