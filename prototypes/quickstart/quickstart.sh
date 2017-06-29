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

declare -A INSTALLER_MAP
declare -A SCENARIO_MAP

# Temp hard coded INSTALLER_MAP SCENARIO_MAP, rank by installer's name in
# alphabetic order.
# Write another script to generate these maps later, will rank installer
# based on ci daily scores and user install history
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
INSTALLERS="apex armada compass daisy fuel joid"
SCENARIOS="os-nosdn-nofeature-ha"
SCENARIOS="${SCENARIOS} os-nosdn-lxd-ha"

# Temp hard coded, select according ci daily scores and user install history
DEFAULT_INSTALLER="apex"
DEFAULT_SCENARIO="os-nosdn-nofeature-ha"

INSTALLER=""
SCENARIO=""
OS_VERION=""
DEPLOY_CMD=""

function parse_args()
{
    :
    # 1. no arg(all args have default value)
    # 2. scenario arg
    # 3. installer arg
    # 4. debug arg
    # 5. push status flag
}

function check_OS_version()
{
    DISTRO=""
    DISTRO_VERSION=""

    OS=$(uname)
    if [ "${OS}" = "Linux" ] ; then
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

    echo "Please run the scripts on Centos 7 or Ubuntu 14.04 or Ubuntu 16.04"
    exit 1
}

function check_mem_size()
{
    mem_size=$(free -h | awk '/Mem\:/ { print int($2) }')
    if [[ "$mem_size" -lt "$VM_MIN_MEM_SIZE" ]]; then
        echo "Run VM deploy needs at least $VM_MIN_MEM_SIZE GB Memory we only have $mem_size GB"
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
    INSTALLER=${INSTALLER:-"$DEFAULT_INSTALLER"}
    SCENARIO=${SCENARIO:-"$DEFAULT_SCENARIO"}
}

function create_workspace()
{
    mkdir -p /opt/opnfv/workspace
    cd /opt/opnfv/workspace
}

function generate_apex_deploy_command()
{
    DEPLOY_CMD="curl https://get.opnfv.org/ephrates/apex/quickstart.sh | SCENARIO=${SCENARIO} bash"
}

function generate_armada_deploy_command()
{
    DEPLOY_CMD="curl https://get.opnfv.org/ephrates/armada/quickstart.sh | SCENARIO=${SCENARIO} bash"
}
function generate_compass_deploy_command()
{
    DEPLOY_CMD="curl https://get.opnfv.org/ephrates/compass/quickstart.sh | SCENARIO=${SCENARIO} bash"
}
function generate_daisy_deploy_command()
{
    DEPLOY_CMD="curl https://get.opnfv.org/ephrates/daisy/quickstart.sh | SCENARIO=${SCENARIO} bash"
}

function generate_fuel_deploy_command()
{
    DEPLOY_CMD="curl https://get.opnfv.org/ephrates/fuel/quickstart.sh | SCENARIO=${SCENARIO} bash"
}

function generate_joid_deploy_command()
{
    DEPLOY_CMD="curl https://get.opnfv.org/ephrates/joid/quickstart.sh | SCENARIO=${SCENARIO} bash"
}

function generate_deploy_cmd()
{
    eval "generate_${INSTALLER}_deploy_command"
}

function raise_message()
{
    echo "Deploy Failed!"
    # print error message
    # info send error to the opnfv-users mailing list with the installer tag
    # and CC installer PTL
}

function exec_deploy_cmd()
{
    eval "$DEPLOY_CMD"
    if [[ $? != 0 ]]; then
        raise_message
    fi

    # may push deploy status to testapi
}

function run_healthcheck()
{
    :
    # boot to vm and ping each other
    # or run functest vping
    # may push health check status to testapi
}

function info_deploy_finished()
{
    echo "Deploy success!"
}

function main()
{
    parse_args
    check_env
    select_installer
    create_workspace
    generate_deploy_cmd
    exec_deploy_cmd
    run_healthcheck
    info_deploy_finished
}

main

