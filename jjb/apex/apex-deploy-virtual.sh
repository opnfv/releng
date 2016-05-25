#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Starting the Apex virtual deployment."
echo "--------------------------------------------------------"
echo

if [[ $BUILD_DIRECTORY == *verify-master* ]]; then
    cd $WORKSPACE/../${BUILD_DIRECTORY/build_output/}
    WORKSPACE=$(pwd)
    echo "WORKSPACE modified to $WORKSPACE"
    cd $WORKSPACE/ci
elif [[ ! "$ARTIFACT_NAME" == "latest" ]]; then
    # if artifact name is passed the pull a
    # specific artifact from artifacts.opnfv.org
    RPM_INSTALL_PATH=$GS_URL
    RPM_LIST=$RPM_INSTALL_PATH/$ARTIFACT_NAME
else
    if [[ $BUILD_DIRECTORY == *verify* ]]; then
      BUILD_DIRECTORY=$WORKSPACE/../$BUILD_DIRECTORY
      echo "BUILD DIRECTORY modified to $BUILD_DIRECTORY"
    elif [[ $BUILD_DIRECTORY == *apex-build* ]]; then
      BUILD_DIRECTORY=$WORKSPACE/../$BUILD_DIRECTORY
      echo "BUILD DIRECTORY modified to $BUILD_DIRECTORY"
    fi

    if [[ -f ${BUILD_DIRECTORY}/../opnfv.properties ]]; then
        # if opnfv.properties exists then use the
        # local build. Source the file so we get local OPNFV vars
        source ${BUILD_DIRECTORY}/../opnfv.properties
        RPM_INSTALL_PATH=${BUILD_DIRECTORY}/noarch
        RPM_LIST=$RPM_INSTALL_PATH/$(basename $OPNFV_RPM_URL)
    else
        if [[ $BUILD_DIRECTORY == *verify* ]]; then
          echo "BUILD_DIRECTORY is from a verify job, so will not use latest from URL"
          echo "Check that the slave has opnfv.properties in $BUILD_DIRECTORY"
          exit 1
        elif [[ $BUILD_DIRECTORY == *apex-build* ]]; then
          echo "BUILD_DIRECTORY is from a daily job, so will not use latest from URL"
          echo "Check that the slave has opnfv.properties in $BUILD_DIRECTORY"
          exit 1
        fi
        # no opnfv.properties means use the latest from artifacts.opnfv.org
        # get the latest.properties to get the link to the latest artifact
        curl -s -o $WORKSPACE/opnfv.properties http://$GS_URL/latest.properties
        [[ -f opnfv.properties ]] || exit 1
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
if [[ $BUILD_DIRECTORY == *verify-master* ]]; then
    if [ ! -e "${WORKSPACE}/build/lib" ]; then ln -s ${WORKSPACE}/lib ${WORKSPACE}/build/lib; fi
    DEPLOY_CMD="CONFIG=${WORKSPACE}/build RESOURCES=${WORKSPACE}/build/images/ ./deploy.sh -c ${WORKSPACE}/build -r ${WORKSPACE}/build/images/"
    DEPLOY_FILE="${WORKSPACE}/config/deploy/${DEPLOY_SCENARIO}.yaml"
    NETWORK_FILE="${WORKSPACE}/config/network/network_settings.yaml"
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
else
    VERSION_EXTENSION=$(echo $(basename $RPM_LIST) | sed 's/opnfv-apex-//')
    for pkg in common undercloud opendaylight-sfc onos; do
        RPM_LIST+=" ${RPM_INSTALL_PATH}/opnfv-apex-${pkg}-${VERSION_EXTENSION}"
    done

    # update / install the new rpm
    if rpm -q opnfv-apex > /dev/null; then
       INSTALLED_RPMS=$(rpm -qa | grep apex)
       for x in $INSTALLED_RPMS; do
         INSTALLED_RPM_VER=$(echo $x | sed 's/opnfv-apex-//').rpm
         # Does each RPM's version match the version required for deployment
         if [ "$INSTALLED_RPM_VER" == "$VERSION_EXTENSION" ]; then
           echo "RPM $x is already installed"
         else
           echo "RPM $x does not match $VERSION_EXTENSION"
           echo "Will upgrade/downgrade RPMs..."
           # Try to upgrade/downgrade RPMS
           if sudo yum update -y $RPM_LIST | grep "does not update installed package"; then
             if ! sudo yum downgrade -y $RPM_LIST; then
               sudo yum remove -y opnfv-apex-undercloud opnfv-apex-common opnfv-apex-opendaylight-sfc opnfv-apex-onos
               sudo yum downgrade -y $RPM_INSTALL_PATH
             fi
           fi
           break
         fi
       done
    else
       sudo yum install -y $RPM_LIST;
    fi
    DEPLOY_CMD=opnfv-deploy
    DEPLOY_FILE="/etc/opnfv-apex/${DEPLOY_SCENARIO}.yaml"
    NETWORK_FILE="/etc/opnfv-apex/network_settings.yaml"
    export RESOURCES="/var/opt/opnfv/images"
    export CONFIG="/var/opt/opnfv"
fi

if [ "$OPNFV_CLEAN" == 'yes' ]; then
    if [[ $BUILD_DIRECTORY == *verify-master* ]]; then
        sudo CONFIG=${WORKSPACE}/build ./clean.sh
    else
        sudo opnfv-clean
    fi
fi
# initiate virtual deployment
echo "Deploy Scenario set to ${DEPLOY_SCENARIO}"
if [ -e $DEPLOY_FILE ]; then
  sudo $DEPLOY_CMD -v -d ${DEPLOY_FILE} -n $NETWORK_FILE --debug
else
  echo "File does not exist /etc/opnfv-apex/${DEPLOY_SCENARIO}.yaml"
  exit 1
fi
echo
echo "--------------------------------------------------------"
echo "Done!"
