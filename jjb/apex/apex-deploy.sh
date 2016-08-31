#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

APEX_PKGS="common undercloud opendaylight-sfc onos"
IPV6_FLAG=False

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
    RESOURCES="${WORKSPACE}/build/images/"
    CONFIG="${WORKSPACE}/build"
    LIB="${WORKSPACE}/lib"
    # Make sure python34 deps are installed
    for dep_pkg in epel-release python34 python34-PyYAML python34-setuptools; do
      if ! rpm -q ${dep_pkg} > /dev/null; then
        if ! sudo yum install -y ${dep_pkg}; then
          echo "Failed to install ${dep_pkg}"
          exit 1
        fi
      fi
    done

    # Make sure jinja2 is installed
    for python_pkg in jinja2; do
      if ! python3.4 -c "import $python_pkg"; then
        echo "$python_pkg package not found for python3.4, attempting to install..."
        if ! sudo easy_install-3.4 $python_pkg; then
          echo -e "Failed to install $python_pkg package for python3.4"
          exit 1
        fi
      fi
    done

    # Make sure ipxe-roms-qemu package is updated to latest.
    # This package is needed for multi virtio nic PXE boot in virtual environment.
    sudo yum update -y ipxe-roms-qemu

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

    DEPLOY_CMD=opnfv-deploy
    DEPLOY_SETTINGS_DIR="/etc/opnfv-apex/"
    NETWORK_SETTINGS_DIR="/etc/opnfv-apex/"
    RESOURCES="/var/opt/opnfv/images"
    CONFIG="/var/opt/opnfv"
    LIB="/var/opt/opnfv/lib"
fi

# set env vars to deploy cmd
DEPLOY_CMD="CONFIG=${CONFIG} RESOURCES=${RESOURCES} LIB=${LIB} ${DEPLOY_CMD}"

if [ "$OPNFV_CLEAN" == 'yes' ]; then
  if sudo test -e '/root/inventory/pod_settings.yaml'; then
    clean_opts='-i /root/inventory/pod_settings.yaml'
  else
    clean_opts=''
  fi
  if [[ "$BUILD_DIRECTORY" == *verify* ]]; then
    sudo CONFIG=${CONFIG} LIB=${LIB} ./clean.sh ${clean_opts}
  else
    sudo CONFIG=${CONFIG} LIB=${LIB} opnfv-clean ${clean_opts}
  fi
fi

if echo ${DEPLOY_SCENARIO} | grep ipv6; then
  IPV6_FLAG=True
  DEPLOY_SCENARIO=$(echo ${DEPLOY_SCENARIO} |  sed 's/-ipv6//')
  echo "INFO: IPV6 Enabled"
fi

echo "Deploy Scenario set to ${DEPLOY_SCENARIO}"
DEPLOY_FILE="${DEPLOY_SETTINGS_DIR}/${DEPLOY_SCENARIO}.yaml"

if [ ! -e "$DEPLOY_FILE" ]; then
  echo "ERROR: Required settings file missing: Deploy settings file ${DEPLOY_FILE}"
fi

if [[ "$JOB_NAME" == *virtual* ]]; then
  # settings for virtual deployment
  if [ "$IPV6_FLAG" == "True" ]; then
    NETWORK_FILE="${NETWORK_SETTINGS_DIR}/network_settings_v6.yaml"
  else
    NETWORK_FILE="${NETWORK_SETTINGS_DIR}/network_settings.yaml"
  fi
  DEPLOY_CMD="${DEPLOY_CMD} -v"
else
  # settings for bare metal deployment
  if [ "$IPV6_FLAG" == "True" ]; then
    NETWORK_FILE="/root/network/network_settings_v6.yaml"
  else
    NETWORK_FILE="/root/network/network_settings.yaml"
  fi
  INVENTORY_FILE="/root/inventory/pod_settings.yaml"

  if ! sudo test -e "$INVENTORY_FILE"; then
    echo "ERROR: Required settings file missing: Inventory settings file ${INVENTORY_FILE}"
    exit 1
  fi
  # include inventory file for bare metal deployment
  DEPLOY_CMD="${DEPLOY_CMD} -i ${INVENTORY_FILE}"
fi

# Check that network settings file exists
if ! sudo test -e "$NETWORK_FILE"; then
  echo "ERROR: Required settings file missing: Network Settings file ${NETWORK_FILE}"
  exit 1
fi

# start deployment
sudo ${DEPLOY_CMD} -d ${DEPLOY_FILE} -n ${NETWORK_FILE} --debug

echo
echo "--------------------------------------------------------"
echo "Done!"
