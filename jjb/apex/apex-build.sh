#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
# log info to console
echo "Starting the build of Apex using OpenStack Master packages. This will take some time..."
echo "---------------------------------------------------------------------------------------"
echo
echo "Checking for Squid Proxy"
if ! systemctl squid status; then
    echo "Squid Not Running, Cannot continue"
    exit 1
fi

# export http_proxy so that we cache somethings
declare -A node_ips
node_ips=(["intel-virtual-3"]=10.2.117.111 
          ["intel-virtual-4"]=10.2.117.117
          ["intel-virtual-5"]=10.2.117.119
          ["lf-pod1"]=172.30.9.66)
http_proxy=http://$node_ips[$NODE_NAME]:3128/

# create the cache directory if it doesn't exist
[[ -d $CACHE_DIRECTORY ]] || mkdir -p $CACHE_DIRECTORY
# set OPNFV_ARTIFACT_VERSION
if echo $BUILD_TAG | grep "apex-verify" 1> /dev/null; then
  export OPNFV_ARTIFACT_VERSION=dev${BUILD_NUMBER}
  export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c $CACHE_DIRECTORY"
elif [ "$ARTIFACT_VERSION" == "daily" ]; then
  export OPNFV_ARTIFACT_VERSION=$(date -u +"%Y-%m-%d")
  export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c $CACHE_DIRECTORY --iso"
else
  export OPNFV_ARTIFACT_VERSION=${ARTIFACT_VERSION}
  export BUILD_ARGS="-r $OPNFV_ARTIFACT_VERSION -c $CACHE_DIRECTORY --iso"
fi

# start the build
cd $WORKSPACE/ci
./build.sh $BUILD_ARGS
RPM_VERSION=$(grep Version: $BUILD_DIRECTORY/rpm_specs/opnfv-apex.spec | awk '{ print $2 }')-$(echo $OPNFV_ARTIFACT_VERSION | tr -d '_-')
# list the contents of BUILD_OUTPUT directory
echo "Build Directory is ${BUILD_DIRECTORY}"
echo "Build Directory Contents:"
echo "-------------------------"
ls -al $BUILD_DIRECTORY

# list the contents of CACHE directory
echo "Cache Directory is ${CACHE_DIRECTORY}"
echo "Cache Directory Contents:"
echo "-------------------------"
ls -al $CACHE_DIRECTORY

if ! echo $BUILD_TAG | grep "apex-verify" 1> /dev/null; then
  echo "Writing opnfv.properties file"
  # save information regarding artifact into file
  (
    echo "OPNFV_ARTIFACT_VERSION=$OPNFV_ARTIFACT_VERSION"
    echo "OPNFV_GIT_URL=$(git config --get remote.origin.url)"
    echo "OPNFV_GIT_SHA1=$(git rev-parse HEAD)"
    echo "OPNFV_ARTIFACT_URL=$GS_URL/opnfv-$OPNFV_ARTIFACT_VERSION.iso"
    echo "OPNFV_ARTIFACT_SHA512SUM=$(sha512sum $BUILD_DIRECTORY/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso | cut -d' ' -f1)"
    echo "OPNFV_SRPM_URL=$GS_URL/opnfv-apex-$RPM_VERSION.src.rpm"
    echo "OPNFV_RPM_URL=$GS_URL/opnfv-apex-$RPM_VERSION.noarch.rpm"
    echo "OPNFV_RPM_SHA512SUM=$(sha512sum $BUILD_DIRECTORY/noarch/opnfv-apex-$RPM_VERSION.noarch.rpm | cut -d' ' -f1)"
    echo "OPNFV_BUILD_URL=$BUILD_URL"
  ) > $WORKSPACE/opnfv.properties
fi
echo "--------------------------------------------------------"
echo "Done!"
