#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
# log info to console
echo "Starting the build of Apex using OpenStack Master packages. This will take some time..."
echo "---------------------------------------------------------------------------------------"
echo
# create the cache directory if it doesn't exist
[[ -d $CACHE_DIRECTORY ]] || mkdir -p $CACHE_DIRECTORY
# set OPNFV_ARTIFACT_VERSION
if echo $ARTIFACT_VERSION | grep "dev" 1> /dev/null; then
  GERRIT_PATCHSET_NUMBER=$(echo $GERRIT_REFSPEC | grep -Eo '[0-9]+$')
  export OPNFV_ARTIFACT_VERSION="dev${GERRIT_CHANGE_NUMBER}_${GERRIT_PATCHSET_NUMBER}"
  export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c $CACHE_DIRECTORY"
elif echo $BUILD_TAG | grep "csit" 1> /dev/null; then
  export OPNFV_ARTIFACT_VERSION=csit${BUILD_NUMBER}
  export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c $CACHE_DIRECTORY"
elif [ "$ARTIFACT_VERSION" == "daily" ]; then
  export OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d")
  if [ "$BRANCH" == 'master' ]; then
    export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c $CACHE_DIRECTORY"
  else
    export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c $CACHE_DIRECTORY --iso"
  fi
else
  export OPNFV_ARTIFACT_VERSION=${ARTIFACT_VERSION}
  if [ "$BRANCH" == 'master' ]; then
    export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c $CACHE_DIRECTORY"
  else
    export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c $CACHE_DIRECTORY --iso"
  fi
fi

# Temporary hack until we fix apex build script
BUILD_DIRECTORY=${WORKSPACE}/build

# start the build
pushd ${BUILD_DIRECTORY}
make clean
popd
export PYTHONPATH=${WORKSPACE}
python3 apex/build.py $BUILD_ARGS
RPM_VERSION=$(grep Version: $WORKSPACE/build/rpm_specs/opnfv-apex.spec | awk '{ print $2 }')-$(echo $OPNFV_ARTIFACT_VERSION | tr -d '_-')
# list the contents of BUILD_OUTPUT directory
echo "Build Directory is ${BUILD_DIRECTORY}/../.build"
echo "Build Directory Contents:"
echo "-------------------------"
ls -al ${BUILD_DIRECTORY}/../.build

# list the contents of CACHE directory
echo "Cache Directory is ${CACHE_DIRECTORY}"
echo "Cache Directory Contents:"
echo "-------------------------"
ls -al $CACHE_DIRECTORY

if [[ "$BUILD_ARGS" =~ '--iso' && "$BRANCH" != 'master' ]]; then
  mkdir -p /tmp/apex-iso/
  rm -f /tmp/apex-iso/*.iso
  cp -f $BUILD_DIRECTORY/../.build/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso /tmp/apex-iso/
fi

if ! echo $ARTIFACT_VERSION | grep "dev" 1> /dev/null; then
  echo "Writing opnfv.properties file"
  if [ "$BRANCH" != master ]; then
    # save information regarding artifact into file
    (
      echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
      echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
      echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
      echo "OPNFV_ARTIFACT_URL=$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
      echo "OPNFV_ARTIFACT_SHA512SUM=$(sha512sum $BUILD_DIRECTORY/../.build/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso | cut -d' ' -f1)"
      echo "OPNFV_SRPM_URL=$GS_URL/opnfv-apex-$RPM_VERSION.src.rpm"
      echo "OPNFV_RPM_URL=$GS_URL/opnfv-apex-$RPM_VERSION.noarch.rpm"
      echo "OPNFV_RPM_SHA512SUM=$(sha512sum $BUILD_DIRECTORY/../.build/noarch/opnfv-apex-$RPM_VERSION.noarch.rpm | cut -d' ' -f1)"
      echo "OPNFV_BUILD_URL=$BUILD_URL"
    ) > $WORKSPACE/opnfv.properties
  else
    # save information regarding artifact into file
    # we only generate the python package for master
    (
      echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
      echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
      echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
      echo "OPNFV_SRPM_URL=$GS_URL/python34-opnfv-apex-$RPM_VERSION.src.rpm"
      echo "OPNFV_RPM_URL=$GS_URL/python34-opnfv-apex-$RPM_VERSION.noarch.rpm"
      echo "OPNFV_RPM_SHA512SUM=$(sha512sum $BUILD_DIRECTORY/../.build/noarch/python34-opnfv-apex-$RPM_VERSION.noarch.rpm | cut -d' ' -f1)"
      echo "OPNFV_BUILD_URL=$BUILD_URL"
    ) > $WORKSPACE/opnfv.properties
  fi
fi
echo "--------------------------------------------------------"
echo "Done!"
