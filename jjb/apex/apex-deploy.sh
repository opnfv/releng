#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

IPV6_FLAG=False

# log info to console
echo "Starting the Apex deployment."
echo "--------------------------------------------------------"
echo

if [ -z "$DEPLOY_SCENARIO" ]; then
  echo "Deploy scenario not set!"
  exit 1
else
  echo "Deploy scenario: ${DEPLOY_SCENARIO}"
fi

# Dev or RPM/ISO build
if [[ "$ARTIFACT_VERSION" =~ dev ]]; then
  # Settings for deploying from git workspace
  DEPLOY_SETTINGS_DIR="${WORKSPACE}/config/deploy"
  NETWORK_SETTINGS_DIR="${WORKSPACE}/config/network"
  CLEAN_CMD="opnfv-clean"
  # if we are using master, then we are downloading/caching upstream images
  # we want to use that built in mechanism to avoid re-downloading every job
  # so we use a dedicated folder to hold the upstream cache
  UPSTREAM_CACHE=$HOME/upstream_cache
  if [ "$BRANCH" == 'master' ]; then
    mkdir -p ${UPSTREAM_CACHE}
    RESOURCES=$UPSTREAM_CACHE
  else
    RESOURCES="${WORKSPACE}/.build/"
  fi
  CONFIG="${WORKSPACE}/build"
  BASE=$CONFIG
  IMAGES=$RESOURCES
  LIB="${WORKSPACE}/lib"
  DEPLOY_CMD="opnfv-deploy --image-dir ${RESOURCES}"
  # Ensure artifacts were downloaded and extracted correctly
  # TODO(trozet) add verification here

  # Install dev build
  sudo rm -rf /tmp/.build
  mv -f .build /tmp/
  sudo pip3 install --upgrade --force-reinstall .
  mv -f /tmp/.build ${WORKSPACE}/
else
  DEPLOY_SETTINGS_DIR="/etc/opnfv-apex/"
  NETWORK_SETTINGS_DIR="/etc/opnfv-apex/"
  CLEAN_CMD="opnfv-clean"
  # set to use different directory here because upon RPM removal this
  # directory will be wiped in daily
  UPSTREAM_CACHE=$HOME/upstream_cache
  if [ "$BRANCH" == 'master' ]; then
    mkdir -p ${UPSTREAM_CACHE}
    RESOURCES=$UPSTREAM_CACHE
  else
    RESOURCES="/var/opt/opnfv/images"
  fi
  DEPLOY_CMD="opnfv-deploy --image-dir ${RESOURCES}"
  CONFIG="/var/opt/opnfv"
  BASE=$CONFIG
  IMAGES=$RESOURCES
  LIB="/var/opt/opnfv/lib"
  sudo mkdir -p /var/log/apex
  sudo chmod 777 /var/log/apex
  cd /var/log/apex
fi

# Install Dependencies
# Make sure python34 dependencies are installed
dependencies="epel-release python34 python34-devel libvirt-devel python34-pip \
ansible python34-PyYAML python34-jinja2 python34-setuptools python-tox ansible"

for dep_pkg in $dependencies; do
  if ! rpm -q ${dep_pkg} > /dev/null; then
    if ! sudo yum install -y ${dep_pkg}; then
      echo "Failed to install ${dep_pkg}"
      exit 1
    fi
  fi
done

if [[ "$JOB_NAME" =~ "virtual" ]]; then
  # Make sure ipxe-roms-qemu package is updated to latest.
  # This package is needed for multi virtio nic PXE boot in virtual environment.
  sudo yum update -y ipxe-roms-qemu
fi

if [ "$OPNFV_CLEAN" == 'yes' ]; then
  if sudo test -e '/root/inventory/pod_settings.yaml'; then
    clean_opts='-i /root/inventory/pod_settings.yaml'
  else
    clean_opts=''
  fi

  sudo ${CLEAN_CMD} ${clean_opts}
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
  if [[ "$PROMOTE" == "True" ]]; then
    DEPLOY_CMD="${DEPLOY_CMD} --virtual-computes 2 -e csit-environment.yaml"
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

if [[ "$BRANCH" == "master" ]]; then
  echo "Upstream deployment detected"
  DEPLOY_CMD="${DEPLOY_CMD} --upstream"
fi

if [ "$IPV6_FLAG" == "True" ]; then
  NETWORK_FILE="${NETWORK_SETTINGS_DIR}/network_settings_v6.yaml"
elif [[ "$PROMOTE" == "True" ]]; then
  NETWORK_FILE="${NETWORK_SETTINGS_DIR}/network_settings_csit.yaml"
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

echo
echo "--------------------------------------------------------"
echo "Done!"
