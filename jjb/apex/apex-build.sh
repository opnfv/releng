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
if echo $BUILD_TAG | grep "apex-verify" 1> /dev/null; then
  if echo $GERRIT_BRANCH | grep "brahmaputra" 1> /dev/null; then
    export OPNFV_ARTIFACT_VERSION=brahmaputra-dev${BUILD_NUMBER}
    export BUILD_ARGS="-v $OPNFV_ARTIFACT_VERSION -c file://$CACHE_DIRECTORY $BUILD_DIRECTORY"
  else
    export OPNFV_ARTIFACT_VERSION=dev${BUILD_NUMBER}
    export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c file://$CACHE_DIRECTORY"
  fi
elif [ "$ARTIFACT_VERSION" == "daily" ]; then
  if echo $GERRIT_BRANCH | grep "brahmaputra" 1> /dev/null; then
    export OPNFV_ARTIFACT_VERSION=brahmaputra-$(date -u +"%Y-%m-%d")
    export BUILD_ARGS="-v $OPNFV_ARTIFACT_VERSION -c file://$CACHE_DIRECTORY $BUILD_DIRECTORY"
  else
    export OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d")
    export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c file://$CACHE_DIRECTORY --iso"
  fi
else
  export OPNFV_ARTIFACT_VERSION=${ARTIFACT_VERSION}
  if echo $GERRIT_BRANCH | grep "brahmaputra" 1> /dev/null; then
    export BUILD_ARGS="-v $OPNFV_ARTIFACT_VERSION -c file://$CACHE_DIRECTORY $BUILD_DIRECTORY"
  else
    export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c file://$CACHE_DIRECTORY --iso"
  fi
fi
# clean for stable but doesn't matter for master
if echo $GERRIT_BRANCH | grep "brahmaputra" 1> /dev/null; then
  sudo opnfv-clean
fi
# start the build
cd $WORKSPACE/ci
./build.sh $BUILD_ARGS
RPM_VERSION=$(grep Version: $BUILD_DIRECTORY/opnfv-apex.spec | awk '{ print $2 }')-$(echo $OPNFV_ARTIFACT_VERSION | tr -d '_-')
# list the contents of BUILD_OUTPUT directory
ls -al $BUILD_DIRECTORY
# save information regarding artifact into file
(
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
    echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
    echo "OPNFV_ARTIFACT_URL=$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
    echo "OPNFV_ARTIFACT_MD5SUM=$(md5sum $BUILD_DIRECTORY/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso | cut -d' ' -f1)"
    echo "OPNFV_SRPM_URL=$GS_URL/opnfv-apex-$RPM_VERSION.src.rpm"
    echo "OPNFV_RPM_URL=$GS_URL/opnfv-apex-$RPM_VERSION.noarch.rpm"
    echo "OPNFV_RPM_MD5SUM=$(md5sum $BUILD_DIRECTORY/noarch/opnfv-apex-$RPM_VERSION.noarch.rpm | cut -d' ' -f1)"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
) > $WORKSPACE/opnfv.properties
echo "--------------------------------------------------------"
echo "Done!"
