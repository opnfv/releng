#!/bin/bash

set -e
set +u
set +o pipefail

REPO=${REPO:-opnfv}
CI_LOOP=${CI_LOOP:-daily}
TEST_DB_URL=http://testresults.opnfv.org/test/api/v1/results
ENERGY_RECORDER_API_URL=http://energy.opnfv.fr/resources
DOCKER_TAG=${DOCKER_TAG:-$([[ ${BRANCH##*/} == "master" ]] && echo "latest" || echo ${BRANCH##*/})}

run_tiers() {
    tiers=$1
    cmd_opt="run_tests -r -t all"
    [[ $BUILD_TAG =~ "suite" ]] && cmd_opt="run_tests -t all"
    for tier in ${tiers[@]}; do
        FUNCTEST_IMAGE=${REPO}/functest-${tier}:${DOCKER_TAG}
        echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
        docker pull ${FUNCTEST_IMAGE}>/dev/null
        cmd="docker run --rm  ${envs} ${volumes} ${TESTCASE_OPTIONS} ${FUNCTEST_IMAGE} /bin/bash -c '${cmd_opt}'"
        echo "Running Functest tier '${tier}'. CMD: ${cmd}"
        eval ${cmd}
        ret_value=$?
        if [ ${ret_value} != 0 ]; then
            echo ${ret_value} > ${ret_val_file}
            if [ ${tier} == 'healthcheck' ]; then
                echo "Healthcheck tier failed. Exiting Functest..."
                skip_tests=1
                break
            fi
        fi
    done
}

run_test() {
    test_name=$1
    cmd_opt="run_tests -t ${test_name}"
    # Determine which Functest image should be used for the test case
    case ${test_name} in
        connection_check|tenantnetwork1|tenantnetwork2|vmready1|vmready2|singlevm1|singlevm2|vping_ssh|vping_userdata|cinder_test|odl|api_check|snaps_health_check|tempest_smoke)
            FUNCTEST_IMAGE=${REPO}/functest-healthcheck:${DOCKER_TAG} ;;
        neutron-tempest-plugin-api|rally_sanity|refstack_defcore|tempest_full|tempest_scenario|patrole|snaps_smoke|neutron_trunk|networking-bgpvpn|networking-sfc|barbican)
            FUNCTEST_IMAGE=${REPO}/functest-smoke:${DOCKER_TAG} ;;
        rally_full|rally_jobs|shaker|vmtp)
            FUNCTEST_IMAGE=${REPO}/functest-benchmarking:${DOCKER_TAG} ;;
        cloudify|cloudify_ims|heat_ims|vyos_vrouter|juju_epc)
            FUNCTEST_IMAGE=${REPO}/functest-vnf:${DOCKER_TAG} ;;
        doctor-notification|bgpvpn|functest-odl-sfc|barometercollectd|fds|vgpu|stor4nfv_os)
            FUNCTEST_IMAGE=${REPO}/functest-features:${DOCKER_TAG} ;;
        *)
            echo "Unkown test case $test_name"
            exit 1
            ;;
    esac
    echo "Functest: Pulling Functest Docker image ${FUNCTEST_IMAGE} ..."
    docker pull ${FUNCTEST_IMAGE}>/dev/null
    cmd="docker run --rm ${envs} ${volumes} ${TESTCASE_OPTIONS} ${FUNCTEST_IMAGE} /bin/bash -c '${cmd_opt}'"
    echo "Running Functest test case '${test_name}'. CMD: ${cmd}"
    eval ${cmd}
    ret_value=$?
    if [ ${ret_value} != 0 ]; then
      echo ${ret_value} > ${ret_val_file}
    fi
}


redirect="/dev/stdout"
FUNCTEST_DIR=/home/opnfv/functest
DEPLOY_TYPE=baremetal
[[ $BUILD_TAG =~ "virtual" ]] && DEPLOY_TYPE=virt
HOST_ARCH=$(uname -m)

# Prepare OpenStack credentials volume
rc_file=${HOME}/opnfv-openrc.sh

if [[ ${INSTALLER_TYPE} == 'joid' ]]; then
    rc_file=$LAB_CONFIG/admin-openrc
elif [[ ${INSTALLER_TYPE} == 'compass' ]]; then
    cacert_file_vol="-v ${HOME}/os_cacert:${FUNCTEST_DIR}/conf/os_cacert"
    echo "export OS_CACERT=${FUNCTEST_DIR}/conf/os_cacert" >> ${HOME}/opnfv-openrc.sh
elif [[ ${INSTALLER_TYPE} == 'fuel' ]] && [[ "${DEPLOY_SCENARIO}" =~ -ha$ ]]; then
    cacert_file_vol="-v ${HOME}/os_cacert:/etc/ssl/certs/mcp_os_cacert"
fi

rc_file_vol="-v ${rc_file}:${FUNCTEST_DIR}/conf/env_file"

echo "Functest: Start Docker and prepare environment"

echo "Functest: Download images that will be used by test cases"
images_dir="${HOME}/opnfv/functest/images"
download_script=${WORKSPACE}/functest/ci/download_images.sh
chmod +x ${download_script}
${download_script} ${images_dir} ${DEPLOY_SCENARIO} ${HOST_ARCH} 2> ${redirect}

images_vol="-v ${images_dir}:${FUNCTEST_DIR}/images"

dir_result="${HOME}/opnfv/functest/results/${BRANCH##*/}"
mkdir -p ${dir_result}
sudo rm -rf ${dir_result}/*
results_vol="-v ${dir_result}:${FUNCTEST_DIR}/results"
custom_params=
test -f ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG} && custom_params=$(cat ${HOME}/opnfv/functest/custom/params_${DOCKER_TAG})

envs="-e INSTALLER_TYPE=${INSTALLER_TYPE} -e INSTALLER_IP=${INSTALLER_IP} \
    -e NODE_NAME=${NODE_NAME} -e DEPLOY_SCENARIO=${DEPLOY_SCENARIO} \
    -e BUILD_TAG=${BUILD_TAG} -e DEPLOY_TYPE=${DEPLOY_TYPE} -e CI_LOOP=${CI_LOOP} \
    -e TEST_DB_URL=${TEST_DB_URL} -e ENERGY_RECORDER_API_URL=${ENERGY_RECORDER_API_URL}"

ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"

if [ "${INSTALLER_TYPE}" == 'fuel' ]; then
    COMPUTE_ARCH=$(ssh -l ubuntu ${INSTALLER_IP} -i ${SSH_KEY} ${ssh_options} \
        "sudo salt 'cmp*' grains.get cpuarch --out yaml | awk '{print \$2; exit}'")
    IMAGE_PROPERTIES="hw_disk_bus:scsi,hw_scsi_model:virtio-scsi"
    envs="${envs} -e POD_ARCH=${COMPUTE_ARCH}"
fi

if [[ ${INSTALLER_TYPE} == 'fuel' && ${DEPLOY_SCENARIO} == 'os-nosdn-nofeature-noha' ]]; then
    libvirt_vol="-v ${ssh_key}:${FUNCTEST_DIR}/conf/libvirt_key"
    envs="${envs} -e LIBVIRT_USER=ubuntu -e LIBVIRT_KEY_PATH=${FUNCTEST_DIR}/conf/libvirt_key"
fi

if [[ ${INSTALLER_TYPE} == 'compass' && ${DEPLOY_SCENARIO} =~ 'sfc' ]]; then
    ssh_key="/tmp/id_rsa"
    user_config="/tmp/openstack_user_config.yml"
    docker cp compass-tasks:/root/.ssh/id_rsa $ssh_key
    docker cp compass-tasks:/etc/openstack_deploy/openstack_user_config.yml $user_config
    sshkey_vol="-v ${ssh_key}:/root/.ssh/id_rsa"
    userconfig_vol="-v ${user_config}:${user_config}"
    envs="${envs} -e EXTERNAL_NETWORK=${EXTERNAL_NETWORK}"
fi

if [[ ${INSTALLER_TYPE} == 'compass' ]] || [[ ${DEPLOY_SCENARIO} == *"odl"* ]]; then
      envs="${envs} -e SDN_CONTROLLER_RESTCONFPORT=8080"
fi

if [[ ${DEPLOY_SCENARIO} == *"ovs"* ]] || [[ ${DEPLOY_SCENARIO} == *"fdio"* ]]; then
    if [[ -n ${IMAGE_PROPERTIES} ]]; then
        IMAGE_PROPERTIES="${IMAGE_PROPERTIES},hw_mem_page_size:large"
    else
        IMAGE_PROPERTIES="hw_mem_page_size:large"
    fi
    FLAVOR_EXTRA_SPECS="hw:mem_page_size:large"
fi

if [[ -n ${IMAGE_PROPERTIES} ]] || [[ -n ${FLAVOR_EXTRA_SPECS} ]]; then
    envs="${envs} -e IMAGE_PROPERTIES=${IMAGE_PROPERTIES} -e FLAVOR_EXTRA_SPECS=${FLAVOR_EXTRA_SPECS}"
fi

tempest_conf_yaml=$(mktemp)
case ${INSTALLER_TYPE} in
apex)
    cat << EOF > "${tempest_conf_yaml}"
---
compute-feature-enabled:
    shelve: false
    vnc_console: true
    block_migration_for_live_migration: false
identity-feature-enabled:
    api_v2: false
    api_v2_admin: false
image-feature-enabled:
    api_v2: true
    api_v1: false
object-storage:
    operator_role: SwiftOperator
volume:
    storage_protocol: ceph
volume-feature-enabled:
    backup: false
EOF
    ;;
compass)
    cat << EOF > "${tempest_conf_yaml}"
---
compute-feature-enabled:
    shelve: false
    vnc_console: false
    block_migration_for_live_migration: false
    spice_console: true
identity-feature-enabled:
    api_v2: false
    api_v2_admin: false
image-feature-enabled:
    api_v2: true
    api_v1: false
volume:
    storage_protocol: ceph
volume-feature-enabled:
    backup: false
EOF
    ;;
fuel)
    cat << EOF > "${tempest_conf_yaml}"
---
compute-feature-enabled:
    shelve: false
    vnc_console: false
    spice_console: true
identity-feature-enabled:
    api_v2: false
    api_v2_admin: false
image-feature-enabled:
    api_v2: true
    api_v1: false
volume:
    storage_protocol: iSCSI
volume-feature-enabled:
    backup: false
EOF
    ;;
*)
    cat << EOF > "${tempest_conf_yaml}"
---
compute-feature-enabled:
    shelve: false
    vnc_console: false
identity-feature-enabled:
    api_v2: false
    api_v2_admin: false
image-feature-enabled:
    api_v2: true
    api_v1: false
volume:
    storage_protocol: iSCSI
volume-feature-enabled:
    backup: false
EOF
    ;;
esac
case ${BRANCH} in
master)
    cat << EOF >> "${tempest_conf_yaml}"
compute:
    max_microversion: latest
EOF
    ;;
stable/hunter)
    cat << EOF >> "${tempest_conf_yaml}"
compute:
    max_microversion: 2.65
EOF
    ;;
stable/gambia)
    cat << EOF >> "${tempest_conf_yaml}"
compute:
    max_microversion: 2.60
EOF
    ;;
esac
echo "tempest_conf.yaml:" && cat "${tempest_conf_yaml}"

volumes="${images_vol} ${results_vol} ${sshkey_vol} ${libvirt_vol} \
    ${userconfig_vol} ${rc_file_vol} ${cacert_file_vol} \
    -v ${tempest_conf_yaml}:/usr/lib/python2.7/site-packages/functest/opnfv_tests/openstack/tempest/custom_tests/tempest_conf.yaml"

if [[ ${INSTALLER_TYPE} == 'apex' ]]; then
    blacklist_yaml=$(mktemp)
    cat << EOF >> "${blacklist_yaml}"
---
-
    scenarios:
        - os-ovn-nofeature-ha
    tests:
        - neutron_tempest_plugin.api.admin.test_agent_management
        - neutron_tempest_plugin.api.admin.test_dhcp_agent_scheduler
        - patrole_tempest_plugin.tests.api.network.test_agents_rbac
        - patrole_tempest_plugin.tests.api.network.test_networks_rbac.NetworksRbacTest.test_create_network_provider_network_type
        - patrole_tempest_plugin.tests.api.network.test_networks_rbac.NetworksRbacTest.test_create_network_provider_segmentation_id
        - tempest.api.network.admin.test_agent_management
        - tempest.api.network.admin.test_dhcp_agent_scheduler
        - tempest.api.object_storage.test_crossdomain.CrossdomainTest.test_get_crossdomain_policy
-
    scenarios:
        - os-nosdn-nofeature-ha
    tests:
        - tempest.api.object_storage.test_crossdomain.CrossdomainTest.test_get_crossdomain_policy
-
    scenarios:
        - os-nosdn-nofeature-noha
    tests:
        - tempest.api.object_storage.test_crossdomain.CrossdomainTest.test_get_crossdomain_policy
EOF
    volumes="${volumes} -v ${blacklist_yaml}:/usr/lib/python2.7/site-packages/functest/opnfv_tests/openstack/tempest/custom_tests/blacklist.yaml"
fi

ret_val_file="${HOME}/opnfv/functest/results/${BRANCH##*/}/return_value"
echo 0 > ${ret_val_file}

set +e

if [ ${FUNCTEST_MODE} == 'testcase' ]; then
    echo "FUNCTEST_MODE=testcase, FUNCTEST_SUITE_NAME=${FUNCTEST_SUITE_NAME}"
    run_test ${FUNCTEST_SUITE_NAME}
elif [ ${FUNCTEST_MODE} == 'tier' ]; then
    echo "FUNCTEST_MODE=tier, FUNCTEST_TIER=${FUNCTEST_TIER}"
    tiers=(${FUNCTEST_TIER})
    run_tiers ${tiers}
else
    tests=()
    skip_tests=0
    if [ "${HOST_ARCH}" != "aarch64" ]; then
        if [[ ${BRANCH} == "stable/gambia" ]]; then
            tiers=(healthcheck smoke benchmarking features vnf components)
        else
            tiers=(healthcheck smoke benchmarking features vnf)
        fi
    else
        if [[ ${BRANCH} == "stable/gambia" ]]; then
            tiers=(healthcheck smoke benchmarking features components)
        else
            tiers=(healthcheck smoke benchmarking features)
        fi
    fi
    run_tiers ${tiers}
    if [ ${skip_tests} -eq 0 ]; then
        for test in "${tests[@]}"; do
            run_test "$test"
        done
    fi
fi
