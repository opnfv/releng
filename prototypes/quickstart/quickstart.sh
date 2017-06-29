#!/bin/bash
##############################################################################
# Copyright (c) 2017 HUAWEI TECHNOLOGIES CO.,LTD and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

VM_MIN_MEM_SIZE=32 # GB

# Temp scripts pgp keyring path
# TODO: fix the path when the real key is created
PGP_KEYRING=https://raw.githubusercontent.com/opnfv/releng/master/keys/release-keyring.gpg

declare -A INSTALLER_MAP
declare -A SCENARIO_MAP

# Temp hard coded INSTALLER_MAP SCENARIO_MAP, rank by installer's name in
# alphabetic order.
# TODO: Write another script to generate these maps
# will rank installer based on ci daily scores and user install history
INSTALLER_MAP['apex']='os-nosdn-nofeature-ha os-nosdn-fdio-ha'
INSTALLER_MAP['armada']='os-nosdn-nofeature-ha'
INSTALLER_MAP['compass']='os-nosdn-nofeature-ha os-nosdn-openo-ha'
INSTALLER_MAP['daisy']='os-nosdn-nofeature-ha'
INSTALLER_MAP['fuel']='os-nosdn-nofeature-ha'
INSTALLER_MAP['joid']='os-nosdn-nofeature-ha os-nosdn-lxd-ha'
SCENARIO_MAP['os-nosdn-nofeature-ha']="apex armada compass daisy fuel joid"
SCENARIO_MAP['os-nosdn-fdio-ha']="apex"
SCENARIO_MAP['os-nosdn-openo-ha']="compass"
SCENARIO_MAP['os-nosdn-lxd-ha']="joid"

SUPPORT_INSTALLERS="apex armada compass daisy fuel joid"
SUPPORT_SCENARIOS="os-nosdn-nofeature-ha"
SUPPORT_SCENARIOS="${SUPPORT_SCENARIOS} os-nosdn-lxd-ha"

# Temp hard coded, select according ci daily scores and user install history
DEFAULT_INSTALLER="apex"
DEFAULT_SCENARIO="os-nosdn-nofeature-ha"

INSTALLER=""
SCENARIO=""
OS_VERION=""
NO_HEALTH_CHECK="false"

function usage()
{
cat << EOF
`basename $0`: Deploys the OPNFV env

usage: `basename $0` [-s deploy-scenario] [-i deploy-installer] [-h] [-H]

OPTIONS:
  -s  Deploy scenario name
  -i  Deploy installer name
  -h  Print this message and exit
  -H  No health check

EOF
}

function parse_args()
{
    while getopts "s:i:hH" OPTION
    do
        case $OPTION in
            s)
                SCENARIO=${OPTARG}
                ;;
            i)
                INSTALLER=${OPTARG}
                ;;
            h)
                usage
                exit 0
                ;;
            H)
                NO_HEALTH_CHECK="true"
                ;;
            *)
                echo "${OPTION} is not a valid argument."
                exit 0
                ;;
        esac
    done
}

function check_OS_version()
{
    DISTRO=""
    DISTRO_VERSION=""

    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        if [ -f /etc/os-release ] ; then
            DISTRO=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
            DISTRO_VERSION=$(awk -F= '/^VERSION_ID/{print $2}' /etc/os-release)
        fi

        if [[ "$DISTRO" =~ "CentOS Linux" ]] && [[ "$DISTRO_VERSION" =~ "7" ]]; then
            OS_VERION="CentOS7"
        elif [[ "$DISTRO" =~ "Ubuntu" ]] && [[ "$DISTRO_VERSION" =~ "14.04" ]]; then
            OS_VERION="Ubuntu14.04"
        elif [[ "$DISTRO" =~ "Ubuntu" ]] && [[ "$DISTRO_VERSION" =~ "16.04" ]]; then
            OS_VERION="Ubuntu16.04"
        fi

        return
    fi

    echo "Please run the scripts on Centos 7 or Ubuntu 14.04 or Ubuntu 16.04."
    exit 1
}

function check_mem_size()
{
    mem_size=$(free -h | awk '/Mem\:/ { print int($2) }')
    if [[ "$mem_size" -lt "$VM_MIN_MEM_SIZE" ]]; then
        echo "Run VM deploy needs at least $VM_MIN_MEM_SIZE GB Memory we only have $mem_size GB."
        exit 1
    fi
}

function check_env()
{
    check_OS_version
    check_mem_size
}

function select_installer()
{
    if [[ "x$INSTALLER" == "x" ]] && [[ "x$SCENARIO" == "x" ]]; then
        INSTALLER=${INSTALLER:-"$DEFAULT_INSTALLER"}
        SCENARIO=${SCENARIO:-"$DEFAULT_SCENARIO"}
    elif [[ "x$INSTALLER" == "x" ]]; then
        if [[ $SUPPORT_SCENARIOS != *"$SCENARIO"* ]]; then
            echo "Sorry we do not support scenario ${SCENARIO}."
            exit 1
        fi
        INSTALLER=$(echo ${SCENARIO_MAP["$SCENARIO"]} | cut -d " " -f 1)
    elif [[ "x$SCENARIO" == "x" ]]; then
        if [[ $SUPPORT_INSTALLERS != *"$INSTALLER"* ]]; then
            echo "Sorry we do not support installer ${INSTALLER}."
            exit 1
        fi
        SCENARIO=$(echo ${INSTALLER_MAP["$INSTALLER"]} | cut -d " " -f 1)
   fi

   if [[ $SUPPORT_INSTALLERS != *"$INSTALLER"* ]]; then
       echo "Sorry we do not support installer ${INSTALLER}."
       exit 1
   fi
   if [[ ${INSTALLER_MAP["$INSTALLER"]} != *"$SCENARIO"* ]]; then
       echo "Sorry $INSTALLER does not support ${SCENARIO}."
       exit 1
   fi

    echo "The selected installer is ${INSTALLER} with scenario ${SCENARIO}."
}

function create_workspace()
{
    mkdir -p /opt/opnfv/workspace
    cd /opt/opnfv/workspace
    curl $PGP_KEYRING | gpg --import
}

function raise_message()
{
    echo "Deploy Failed!"
    exit 1
    # print error message
    # info send error to the opnfv-users mailing list with the installer tag
    # and CC installer PTL
}

function do_apex_install()
{
    echo "Start apex installing..."
    curl -fsSL get.opnfv.org/ephrates/apex/quickstart.sh -o apex-quickstart.sh
    curl -fsSL get.opnfv.org/ephrates/apex/quickstart.sh.sig -o apex-quickstart.sh.sig
    gpg --verify apex-quickstart.sh.sig apex-quickstart.sh ||
    {
        _return=$?
        echo "Install script signing failed!"
        return $_return
    }
    SCENARIO=${SCENARIO} sh apex-quickstart.sh
}

function do_armada_install()
{
    echo "Start armada installing..."
    curl -fsSL get.opnfv.org/ephrates/armada/quickstart.sh -o armada-quickstart.sh
    curl -fsSL get.opnfv.org/ephrates/armada/quickstart.sh.sig -o armada-quickstart.sh.sig
    gpg --verify armada-quickstart.sh.sig armada-quickstart.sh ||
    {
        _return=$?
        echo "Install script signing failed!"
        return $_return
    }
    SCENARIO=${SCENARIO} sh armada-quickstart.sh
}

function do_compass_install()
{
    echo "Start compass installing..."
    curl -fsSL get.opnfv.org/ephrates/compass/quickstart.sh -o compass-quickstart.sh
    curl -fsSL get.opnfv.org/ephrates/compass/quicktart.sh.sig -o compass-quickstart.sh.sig
    gpg --verify compass-quickstart.sh.sig compass-quickstart.sh ||
    {
        _return=$?
        echo "Install script signing failed!"
        return $_return
    }
    SCENARIO=${SCENARIO} sh compass-quickstart.sh
}

function do_daisy_install()
{
    echo "Start daisy installing..."
    curl -fsSL get.opnfv.org/ephrates/daisy/quickstart.sh -o daisy-quickstart.sh
    curl -fsSL get.opnfv.org/ephrates/daisy/quickstart.sh.sig -o daisy-quickstart.sh.sig
    gpg --verify daisy-quickstart.sh.sig daisy-quickstart.sh ||
    {
        _return=$?
        echo "Install script signing failed!"
        return $_return
    }
    SCENARIO=${SCENARIO} sh daisy-quickstart.sh
}

function do_fuel_install()
{
    echo "Start fuel installing..."
    curl -fsSL get.opnfv.org/ephrates/fuel/quickstart.sh -o fuel-quickstart.sh
    curl -fsSL get.opnfv.org/ephrates/fuel/quickstart.sh.sig -o fuel-quickstart.sh.sig
    gpg --verify fuel-quickstart.sh.sig fuel-quickstart.sh ||
    {
        _return=$?
        echo "Install script signing failed!"
        return $_return
    }
    SCENARIO=${SCENARIO} sh fuel-quickstart.sh
}

function do_joid_install()
{
    echo "Start joid installing..."
    curl -fsSL get.opnfv.org/ephrates/joid/quickstart.sh -o joid-quickstart.sh
    curl -fsSL get.opnfv.org/ephrates/joid/quickstart.sh.sig -o joid-quickstart.sh.sig
    gpg --verify joid-quickstart.sh.sig joid-quickstart.sh ||
    {
        _return=$?
        echo "Install script signing failed!"
        return $_return
    }
    SCENARIO=${SCENARIO} sh joid-quickstart.sh
}

function do_install()
{
    case "$INSTALLER" in
        apex)
            do_apex_install
            ;;
        armada)
            do_armada_install
            ;;
        compass)
            do_compass_install
            ;;
        daisy)
            do_daisy_install
            ;;
        fuel)
            do_fuel_install
            ;;
        joid)
            do_joid_install
            ;;
        *)
            echo "Installer: [${INSTALLER}] does not support quick install!"
            exit 1
    esac

    if [[ $? != 0 ]]; then
        raise_message
    fi

    # TODO: may push deploy status to testapi
}

function do_healthcheck()
{
    if [[ $NO_HEALTH_CHECK =~ "true" ]]; then
        echo "No health check."
        return
    fi
    # TODO: do basic health check
    #   - boot two vms and ping each other or run functest vping test case
    #   - may push health check status to testapi
}

function info_deploy_finished()
{
    echo "Deploy success!"
}

function main()
{
    parse_args "$@"
    check_env
    select_installer
    create_workspace
    do_install
    do_healthcheck
    info_deploy_finished
}

main "$@"

