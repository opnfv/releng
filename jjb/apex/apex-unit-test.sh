#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
# log info to console
echo "Starting unit tests for Apex..."
echo "---------------------------------------------------------------------------------------"
echo

PATH=$PATH:/usr/sbin


pushd build/ > /dev/null
for pkg in yamllint rpmlint iproute epel-release python34-devel python34-nose python34-PyYAML python-pep8 python34-mock python34-pip; do
  if ! rpm -q ${pkg} > /dev/null; then
    if ! sudo yum install -y ${pkg}; then
      echo "Failed to install ${pkg} package..."
      exit 1
    fi
  fi
done

# Make sure coverage is installed
if ! python3 -c "import coverage" &> /dev/null; then sudo pip3 install coverage; fi

make rpmlint
make python-pep8-check
make yamllint
make python-tests
popd > /dev/null

echo "--------------------------------------------------------"
echo "Unit Tests Done!"
