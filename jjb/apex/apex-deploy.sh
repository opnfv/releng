#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

APEX_PKGS="common undercloud" # removed onos for danube
IPV6_FLAG=False

# log info to console
echo "Starting the Apex virtual deployment."
echo "--------------------------------------------------------"
echo

if ! rpm -q wget > /dev/null; then
  sudo yum -y install wget
fi

if [[ "$BUILD_DIRECTORY" == *verify* || "$BUILD_DIRECTORY" == *promote* ]]; then
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
      RPM_INSTALL_PATH=$(echo "http://"$OPNFV_RPM_URL | sed 's/\/'"$(basename $OPNFV_RPM_URL)"'//')
      RPM_LIST=${RPM_INSTALL_PATH}/$(basename $OPNFV_RPM_URL)
    fi
fi

# rename odl_l3 to odl only for master
# this can be removed once all the odl_l3 references
# are updated to odl after the danube jobs are removed
if [[ "$BUILD_DIRECTORY" == *master* ]]; then
    DEPLOY_SCENARIO=${DEPLOY_SCENARIO/odl_l3/odl}
fi
if [ -z "$DEPLOY_SCENARIO" ]; then
  echo "Deploy scenario not set!"
  exit 1
elif [[ "$DEPLOY_SCENARIO" == *gate* ]]; then
  echo "Detecting Gating scenario..."
  if [ -z "$GERRIT_EVENT_COMMENT_TEXT" ]; then
    echo "ERROR: Gate job triggered without comment!"
    exit 1
  else
    DEPLOY_SCENARIO=$(echo ${GERRIT_EVENT_COMMENT_TEXT} | grep start-gate-scenario | grep -Eo 'os-.*$')
    if [ -z "$DEPLOY_SCENARIO" ]; then
      echo "ERROR: Unable to detect scenario in Gerrit Comment!"
      echo "Format of comment to trigger gate should be 'start-gate-scenario: <scenario>'"
      exit 1
    else
      echo "Gate scenario detected: ${DEPLOY_SCENARIO}"
    fi
  fi
fi

# use local build for verify and promote
if [[ "$BUILD_DIRECTORY" == *verify* || "$BUILD_DIRECTORY" == *promote* ]]; then
    if [ ! -e "${WORKSPACE}/build/lib" ]; then
      ln -s ${WORKSPACE}/lib ${WORKSPACE}/build/lib
    fi
    DEPLOY_SETTINGS_DIR="${WORKSPACE}/config/deploy"
    NETWORK_SETTINGS_DIR="${WORKSPACE}/config/network"
    DEPLOY_CMD="$(pwd)/deploy.sh"
    IMAGES="${WORKSPACE}/.build/"
    BASE="${WORKSPACE}/build"
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

    DEPLOY_CMD=opnfv-deploy
    DEPLOY_SETTINGS_DIR="/etc/opnfv-apex/"
    NETWORK_SETTINGS_DIR="/etc/opnfv-apex/"
    IMAGES="/var/opt/opnfv/images"
    BASE="/var/opt/opnfv"
    LIB="/var/opt/opnfv/lib"
fi

# set env vars to deploy cmd
DEPLOY_CMD="BASE=${BASE} IMAGES=${IMAGES} LIB=${LIB} ${DEPLOY_CMD}"

if [ "$OPNFV_CLEAN" == 'yes' ]; then
  if sudo test -e '/root/inventory/pod_settings.yaml'; then
    clean_opts='-i /root/inventory/pod_settings.yaml'
  else
    clean_opts=''
  fi
  if [[ "$BUILD_DIRECTORY" == *verify* || "$BUILD_DIRECTORY" == *promote* ]]; then
    sudo BASE=${BASE} LIB=${LIB} ./clean.sh ${clean_opts}
  else
    sudo BASE=${BASE} LIB=${LIB} opnfv-clean ${clean_opts}
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
  DEPLOY_CMD="${DEPLOY_CMD} -v"
  if [[ "${DEPLOY_SCENARIO}" =~ fdio|ovs ]]; then
    DEPLOY_CMD="${DEPLOY_CMD} --virtual-default-ram 14 --virtual-compute-ram 8"
  fi
  if [[ "$JOB_NAME" == *csit* ]]; then
    DEPLOY_CMD="${DEPLOY_CMD} -e csit-environment.yaml"
  fi
  if [[ "$JOB_NAME" == *promote* ]]; then
    DEPLOY_CMD="${DEPLOY_CMD} --virtual-computes 2"
  fi
else
  # settings for bare metal deployment
  NETWORK_SETTINGS_DIR="/root/network"
  INVENTORY_FILE="/root/inventory/pod_settings.yaml"

# (trozet) According to FDS folks uio_pci_generic works with UCS-B
# and there appears to be a bug with vfio-pci
  # if fdio on baremetal, then we are using UCS enic and
  # need to use vfio-pci instead of uio generic
#  if [[ "$DEPLOY_SCENARIO" == *fdio* ]]; then
#    TMP_DEPLOY_FILE="${WORKSPACE}/${DEPLOY_SCENARIO}.yaml"
#    cp -f ${DEPLOY_FILE} ${TMP_DEPLOY_FILE}
#    sed -i 's/^\(\s*uio-driver:\).*$/\1 vfio-pci/g' ${TMP_DEPLOY_FILE}
#    DEPLOY_FILE=${TMP_DEPLOY_FILE}
#  fi

  if ! sudo test -e "$INVENTORY_FILE"; then
    echo "ERROR: Required settings file missing: Inventory settings file ${INVENTORY_FILE}"
    exit 1
  fi
  # include inventory file for bare metal deployment
  DEPLOY_CMD="${DEPLOY_CMD} -i ${INVENTORY_FILE}"
fi

if [ "$IPV6_FLAG" == "True" ]; then
  NETWORK_FILE="${NETWORK_SETTINGS_DIR}/network_settings_v6.yaml"
elif echo ${DEPLOY_SCENARIO} | grep fdio; then
  NETWORK_FILE="${NETWORK_SETTINGS_DIR}/network_settings_vpp.yaml"
else
  NETWORK_FILE="${NETWORK_SETTINGS_DIR}/network_settings.yaml"
fi

# Check that network settings file exists
if ! sudo test -e "$NETWORK_FILE"; then
  echo "ERROR: Required settings file missing: Network Settings file ${NETWORK_FILE}"
  exit 1
fi

# start deployment
sudo ${DEPLOY_CMD} -d ${DEPLOY_FILE} -n ${NETWORK_FILE} --debug

if [[ "$JOB_NAME" == *csit* ]]; then
  echo "CSIT job: setting host route for floating ip routing"
  # csit route to allow docker container to reach floating ips
  UNDERCLOUD=$(sudo virsh domifaddr undercloud | grep -Eo "[0-9\.]+{3}[0-9]+")
  if sudo route | grep 192.168.37.128 > /dev/null; then
    sudo route del -net 192.168.37.128 netmask 255.255.255.128
  fi
  sudo route add -net 192.168.37.128 netmask 255.255.255.128 gw ${UNDERCLOUD}
fi

echo
echo "--------------------------------------------------------"
echo "Done!"
