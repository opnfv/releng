#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

APEX_PKGS="common undercloud" # removed onos for danube

# log info to console
echo "Downloading the Apex artifact. This could take some time..."
echo "--------------------------------------------------------"
echo

[[ -d $BUILD_DIRECTORY ]] || mkdir -p $BUILD_DIRECTORY

if [[ "$ARTIFACT_VERSION" =~ dev ]]; then
  # dev build
  GERRIT_PATCHSET_NUMBER=$(echo $GERRIT_REFSPEC | grep -Eo '[0-9]+$')
  export OPNFV_ARTIFACT_VERSION="dev${GERRIT_CHANGE_NUMBER}_${GERRIT_PATCHSET_NUMBER}"
  # get build artifact
  pushd ${BUILD_DIRECTORY} > /dev/null
  echo "Downloading packaged dev build: apex-${OPNFV_ARTIFACT_VERSION}.tar.gz"
  curl --fail -s -o $BUILD_DIRECTORY/apex-${OPNFV_ARTIFACT_VERSION}.tar.gz http://$GS_URL/apex-${OPNFV_ARTIFACT_VERSION}.tar.gz
  tar -xvf apex-${OPNFV_ARTIFACT_VERSION}.tar.gz
  popd > /dev/null
else
  echo "Will download RPMs..."

  # Must be RPMs/ISO
  echo "Downloading latest properties file"

  # get the properties file in order to get info regarding artifacts
  curl --fail -s -o $BUILD_DIRECTORY/opnfv.properties http://$GS_URL/latest.properties

  # source the file so we get OPNFV vars
  source $BUILD_DIRECTORY/opnfv.properties

  RPM_INSTALL_PATH=$(echo "http://"$OPNFV_RPM_URL | sed 's/\/'"$(basename $OPNFV_RPM_URL)"'//')
  RPM_LIST=${RPM_INSTALL_PATH}/$(basename $OPNFV_RPM_URL)

  # find version of RPM
  VERSION_EXTENSION=$(echo $(basename $RPM_LIST) | grep -Eo '[0-9]+\.[0-9]+-([0-9]{8}|[a-z]+-[0-9]\.[0-9]+)')
  # build RPM List which already includes base Apex RPM
  for pkg in ${APEX_PKGS}; do
    RPM_LIST+=" ${RPM_INSTALL_PATH}/opnfv-apex-${pkg}-${VERSION_EXTENSION}.noarch.rpm"
  done

  # remove old / install new RPMs
  if rpm -q opnfv-apex > /dev/null; then
    INSTALLED_RPMS=$(rpm -qa | grep apex)
    if [ -n "$INSTALLED_RPMS" ]; then
      sudo yum remove -y ${INSTALLED_RPMS}
    fi
  fi
  if ! sudo yum install -y $RPM_LIST; then
    echo "Unable to install new RPMs: $RPM_LIST"
    exit 1
  fi
fi

# TODO: Uncomment these lines to verify SHA512SUMs once the sums are
# fixed.
# echo "$OPNFV_ARTIFACT_SHA512SUM $BUILD_DIRECTORY/apex.iso" | sha512sum -c
# echo "$OPNFV_RPM_SHA512SUM $BUILD_DIRECTORY/$(basename $OPNFV_RPM_URL)" | sha512sum -c

# list the files
ls -al $BUILD_DIRECTORY

echo
echo "--------------------------------------------------------"
echo "Done!"
