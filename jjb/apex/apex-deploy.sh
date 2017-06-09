#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

APEX_PKGS="common undercloud onos"
IPV6_FLAG=False

# log info to console
echo "Starting the Apex deployment."
echo "--------------------------------------------------------"
echo

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

# Dev or RPM/ISO build
if [[ "$ARTIFACT_VERSION" =~ dev ]]; then
  # Settings for deploying from git workspace
  DEPLOY_SETTINGS_DIR="${WORKSPACE}/config/deploy"
  NETWORK_SETTINGS_DIR="${WORKSPACE}/config/network"
  DEPLOY_CMD="${WORKSPACE}/ci/deploy.sh"
  CLEAN_CMD="${WORKSPACE}/ci/clean.sh"
  RESOURCES="${WORKSPACE}/.build/"
  CONFIG="${WORKSPACE}/build"
  BASE=$CONFIG
  IMAGES=$RESOURCES
  LIB="${WORKSPACE}/lib"

  # Ensure artifacts were downloaded and extracted correctly
  # TODO(trozet) add verification here

else
  DEPLOY_SETTINGS_DIR="/etc/opnfv-apex/"
  NETWORK_SETTINGS_DIR="/etc/opnfv-apex/"
  DEPLOY_CMD="opnfv-deploy"
  CLEAN_CMD="opnfv-clean"
  RESOURCES="/var/opt/opnfv/images"
  CONFIG="/var/opt/opnfv"
  BASE=$CONFIG
  IMAGES=$RESOURCES
  LIB="/var/opt/opnfv/lib"

fi

# Install Dependencies
# Make sure python34 dependencies are installed
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

if [[ "$JOB_NAME" =~ "virtual" ]]; then
  # Make sure ipxe-roms-qemu package is updated to latest.
  # This package is needed for multi virtio nic PXE boot in virtual environment.
  sudo yum update -y ipxe-roms-qemu
  if [ -z ${PYTHONPATH:-} ]; then
    export PYTHONPATH=${WORKSPACE}/lib/python
  else
    export PYTHONPATH=$PYTHONPATH:${WORKSPACE}/lib/python
  fi
fi

# set env vars to deploy cmd
DEPLOY_CMD="BASE=${BASE} IMAGES=${IMAGES} LIB=${LIB} ${DEPLOY_CMD}"

if [ "$OPNFV_CLEAN" == 'yes' ]; then
  if sudo test -e '/root/inventory/pod_settings.yaml'; then
    clean_opts='-i /root/inventory/pod_settings.yaml'
  else
    clean_opts=''
  fi

  sudo BASE=${BASE} LIB=${LIB} ${CLEAN_CMD} ${clean_opts}
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

if [[ "$JOB_NAME" =~ "virtual" ]]; then
  # settings for virtual deployment
  DEPLOY_CMD="${DEPLOY_CMD} -v"
  if [[ "${DEPLOY_SCENARIO}" =~ fdio|ovs ]]; then
    DEPLOY_CMD="${DEPLOY_CMD} --virtual-default-ram 12 --virtual-compute-ram 7"
  fi
  if [[ "$JOB_NAME" == *csit* ]]; then
    DEPLOY_CMD="${DEPLOY_CMD} -e csit-environment.yaml"
  fi
  if [[ "$PROMOTE" == "True" ]]; then
    DEPLOY_CMD="${DEPLOY_CMD} --virtual-computes 2"
  fi
else
  # settings for bare metal deployment
  NETWORK_SETTINGS_DIR="/root/network"
  INVENTORY_FILE="/root/inventory/pod_settings.yaml"

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
