#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Starting the Apex baremetal deployment."
echo "--------------------------------------------------------"
echo

if [[ ! "$ARTIFACT_NAME" == "latest" ]]; then
    # if artifact name is passed the pull a
    # specific artifact from artifacts.opnfv.org
    RPM_INSTALL_PATH=$GS_URL/$ARTIFACT_NAME
else
    if [[ $BUILD_DIRECTORY == *apex-build* ]]; then
      BUILD_DIRECTORY=$WORKSPACE/../$BUILD_DIRECTORY
      echo "BUILD DIRECTORY modified to $BUILD_DIRECTORY"
    fi
    if [[ -f ${BUILD_DIRECTORY}/../opnfv.properties ]]; then
        # if opnfv.properties exists then use the
        # local build. Source the file so we get local OPNFV vars
        source ${BUILD_DIRECTORY}/../opnfv.properties
        RPM_INSTALL_PATH=${BUILD_DIRECTORY}/$(basename $OPNFV_RPM_URL)
    else
        # no opnfv.properties means use the latest from artifacts.opnfv.org
        # get the latest.properties to get the link to the latest artifact
        curl -s -o $WORKSPACE/opnfv.properties http://$GS_URL/latest.properties
        [[ -f opnfv.properties ]] || exit 1
        # source the file so we get OPNFV vars
        source opnfv.properties
        RPM_INSTALL_PATH=$OPNFV_RPM_URL
    fi
fi

if [ ! -e "$RPM_INSTALL_PATH" ]; then
   RPM_INSTALL_PATH=http://${OPNFV_RPM_URL}
fi

RPM_LIST=$RPM_INSTALL_PATH
for pkg in common undercloud; do
    RPM_LIST+=" ${RPM_INSTALL_PATH/opnfv-apex/opnfv-apex-${pkg}}"
done

# update / install the new rpm
if rpm -q opnfv-apex > /dev/null; then
   if [ $(basename $OPNFV_RPM_URL) == $(rpm -q opnfv-apex).rpm ]; then
     echo "RPM is already installed"
   elif sudo yum update -y $RPM_LIST | grep "does not update installed package"; then
       if ! sudo yum downgrade -y $RPM_LIST; then
         sudo yum remove -y opnfv-undercloud opnfv-common
         sudo yum downgrade -y $RPM_INSTALL_PATH
       fi
   fi
else
   sudo yum install -y $RPM_LIST;
fi

# cleanup environment before we start
sudo opnfv-clean
# initiate baremetal deployment
if [ -e /etc/opnfv-apex/network_settings.yaml ]; then
  if [ -n "$DEPLOY_SCENARIO" ]; then
    echo "Deploy Scenario set to ${DEPLOY_SCENARIO}"
    if [ -e /etc/opnfv-apex/${DEPLOY_SCENARIO}.yaml ]; then
      sudo opnfv-deploy -i  /root/inventory/pod_settings.yaml \
      -d /etc/opnfv-apex/${DEPLOY_SCENARIO}.yaml \
      -n /root/network/network_settings.yaml --debug
    else
      echo "File does not exist /etc/opnfv-apex/${DEPLOY_SCENARIO}.yaml"
      exit 1
    fi
  else
    echo "Deploy scenario not set!"
    exit 1
  fi
else
  echo "File /etc/opnfv-apex/network_settings.yaml does not exist!"
  exit 1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"
