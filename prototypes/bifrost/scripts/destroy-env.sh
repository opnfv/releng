#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 RedHat and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# We need to execute everything as root
if [[ $(whoami) != "root" ]]; then
    echo "Error: This script must be run as root!"
    exit 1
fi
# I am afraid of these three VMs in host will have impact on verify
virsh destroy jumphost.opnfvlocal || true
virsh destroy controller00.opnfvlocal || true
virsh destroy compute00.opnfvlocal || true
virsh undefine jumphost.opnfvlocal || true
virsh undefine controller00.opnfvlocal || true
virsh undefine compute00.opnfvlocal || true

virsh destroy jumphost || true
virsh destroy controller00 || true
virsh destroy controller01 || true
virsh destroy controller02 || true
virsh destroy compute00 || true
virsh destroy compute01 || true
virsh undefine jumphost || true
virsh undefine controller00 || true
virsh undefine controller01 || true
virsh undefine controller02 || true
virsh undefine compute00 || true
virsh undefine compute01 || true

service ironic-conductor stop || true

echo "removing ironic database"
if $(which mysql &> /dev/null); then
    mysql -u root ironic --execute "drop database ironic;"
fi
echo "removing leases"
[[ -e /var/lib/misc/dnsmasq/dnsmasq.leases ]] && > /var/lib/misc/dnsmasq/dnsmasq.leases
echo "removing logs"
rm -rf /var/log/libvirt/baremetal_logs/*

# clean up dib images only if requested explicitly
CLEAN_DIB_IMAGES=${CLEAN_DIB_IMAGES:-false}

if [ $CLEAN_DIB_IMAGES = "true" ]; then
    rm -rf /httpboot /tftpboot
    mkdir /httpboot /tftpboot
    chmod -R 755 /httpboot /tftpboot
fi

# remove VM disk images
rm -rf /var/lib/libvirt/images/*.qcow2

echo "restarting services"
service dnsmasq restart || true
service libvirtd restart
service ironic-api restart || true
service ironic-conductor start || true
service ironic-inspector restart || true
