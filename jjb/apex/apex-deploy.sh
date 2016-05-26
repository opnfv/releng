#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

source ./apex-common.sh

APEX_PKGS="common undercloud opendaylight-sfc onos"

# log info to console
echo "Starting the Apex virtual deployment."
echo "--------------------------------------------------------"
echo

if ! rpm -q wget > /dev/null; then
  sudo yum -y install wget
fi

if [[ $BUILD_DIRECTORY == *verify* ]]; then
    # Build is from a verify, use local build artifacts (not RPMs)
    cd $WORKSPACE/../${BUILD_DIRECTORY}
    WORKSPACE=$(pwd)
    echo "WORKSPACE modified to $WORKSPACE"
    cd $WORKSPACE/ci
elif [[ ! "$ARTIFACT_NAME" == "latest" ]]; then
    # if artifact name is passed the pull a
    # specific artifact from artifacts.opnfv.org
    # artifact specified should be opnfv-apex-<version>.noarch.rpm
    RPM_INSTALL_PATH=$GS_URL
    RPM_LIST=$RPM_INSTALL_PATH/$ARTIFACT_NAME
else
    # Use latest RPMS
    if [[ $BUILD_DIRECTORY == *apex-build* ]]; then
      # Triggered from a daily so RPMS should be in local directory
      BUILD_DIRECTORY=$WORKSPACE/../$BUILD_DIRECTORY
      echo "BUILD DIRECTORY modified to $BUILD_DIRECTORY"

      if [[ -f ${BUILD_DIRECTORY}/../opnfv.properties ]]; then
        # if opnfv.properties exists then use the
        # local build. Source the file so we get local OPNFV vars
        source ${BUILD_DIRECTORY}/../opnfv.properties
        RPM_INSTALL_PATH=${BUILD_DIRECTORY}/noarch
        RPM_LIST=$RPM_INSTALL_PATH/$(basename $OPNFV_RPM_URL)
      else
        echo "BUILD_DIRECTORY is from a daily job, so will not use latest from URL"
        echo "Check that the slave has opnfv.properties in $BUILD_DIRECTORY"
        exit 1
      fi
    else
      # use the latest from artifacts.opnfv.org
      # get the latest.properties to get the link to the latest artifact
      if ! wget -O $WORKSPACE/opnfv.properties http://$GS_URL/latest.properties; then
        echo "ERROR: Unable to find latest.properties at ${GS_URL}...exiting"
        exit 1
      fi
      # source the file so we get OPNFV vars
      source opnfv.properties
      RPM_INSTALL_PATH=$(echo $OPNFV_RPM_URL | sed 's/'"$(basename $OPNFV_RPM_URL)"'//')
      RPM_LIST=$RPM_INSTALL_PATH/$(basename $OPNFV_RPM_URL)
    fi
fi

if [ -z "$DEPLOY_SCENARIO" ]; then
  echo "Deploy scenario not set!"
  exit 1
fi

# use local build for verify
if [[ "$BUILD_DIRECTORY" == *verify* ]]; then
    if [ ! -e "${WORKSPACE}/build/lib" ]; then
      ln -s ${WORKSPACE}/lib ${WORKSPACE}/build/lib
    fi
    DEPLOY_SETTINGS_DIR="${WORKSPACE}/config/deploy"
    NETWORK_SETTINGS_DIR="${WORKSPACE}/config/network"
    DEPLOY_CMD="$(pwd)/deploy.sh"
    export RESOURCES="${WORKSPACE}/build/images/"
    export CONFIG="{WORKSPACE}/build"
    # Make sure python34 is installed
    if ! rpm -q python34 > /dev/null; then
        sudo yum install -y epel-release
        if ! sudo yum install -y python34; then
            echo "Failed to install python34"
            exit 1
        fi
    fi
    if ! rpm -q python34-PyYAML > /dev/null; then
        sudo yum install -y epel-release
        if ! sudo yum install -y python34-PyYAML; then
            echo "Failed to install python34-PyYAML"
            exit 1
        fi
    fi
    if ! rpm -q python34-setuptools > /dev/null; then
        if ! sudo yum install -y python34-setuptools; then
            echo "Failed to install python34-setuptools"
            exit 1
        fi
    fi
    if [ -z ${PYTHONPATH:-} ]; then
        export PYTHONPATH=${WORKSPACE}/lib/python
    else
        export PYTHONPATH=$PYTHONPATH:${WORKSPACE}/lib/python
    fi
# use RPMs
else
    # find version of RPM
    VERSION_EXTENSION=$(echo $(basename $RPM_LIST) | grep -Eo '[0-9]+\.[0-9]+-[0-9]{8}')
    # build RPM List which already includes base Apex RPM
    for pkg in ${APEX_PKGS}; do
        RPM_LIST+=" ${RPM_INSTALL_PATH}/opnfv-apex-${pkg}-${VERSION_EXTENSION}.noarch.rpm"
    done

    # update / install the new rpm
    install_rpms

    DEPLOY_CMD=opnfv-deploy
    DEPLOY_SETTINGS_DIR="/etc/opnfv-apex/"
    NETWORK_SETTINGS_DIR="/etc/opnfv-apex/"
    export RESOURCES="/var/opt/opnfv/images"
    export CONFIG="/var/opt/opnfv"
fi

if [ "$OPNFV_CLEAN" == 'yes' ]; then
    if [[ "$BUILD_DIRECTORY" == *verify* ]]; then
        sudo ./clean.sh
    else
        sudo opnfv-clean
    fi
fi

echo "Deploy Scenario set to ${DEPLOY_SCENARIO}"
DEPLOY_FILE="${DEPLOY_SETTINGS_DIR}/${DEPLOY_SCENARIO}.yaml"

if [ ! -e "$DEPLOY_FILE" ]; then
  echo "ERROR: Required settings file missing: Deploy settings file ${DEPLOY_FILE}"
fi

if [[ "$JOB_NAME" == *virtual* ]]; then
  # settings for virtual deployment
  NETWORK_FILE="${NETWORK_SETTINGS_DIR}/network_settings.yaml"
  DEPLOY_CMD="${DEPLOY_CMD} -v"
else
  # settings for bare metal deployment
  NETWORK_FILE="/root/network/network_settings.yaml"
  INVENTORY_FILE="/root/inventory/pod_settings.yaml"

  if [ ! -e "$INVENTORY_FILE" ]; then
    echo "ERROR: Required settings file missing: Inventory settings file ${INVENTORY_FILE}"
  fi
fi

# Check that network settings file exists
if [ ! -e "$NETWORK_FILE" ]; then
  echo "ERROR: Required settings file missing for Network Settings"
  echo "Network settings file: ${NETWORK_FILE}"
  exit 1
fi

# start deployment
sudo ${DEPLOY_CMD} -d ${DEPLOY_FILE} -n ${NETWORK_FILE} --debug

echo
echo "--------------------------------------------------------"
echo "Done!"
