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

virsh destroy jumphost.opnfvlocal || true
virsh destroy controller00.opnfvlocal || true
virsh destroy compute00.opnfvlocal || true
virsh undefine jumphost.opnfvlocal || true
virsh undefine controller00.opnfvlocal || true
virsh undefine compute00.opnfvlocal || true

service ironic-conductor stop

echo "removing from database"
mysql -u root ironic --execute "truncate table ports;"
mysql -u root ironic --execute "delete from node_tags;"
mysql -u root ironic --execute "delete from nodes;"
mysql -u root ironic --execute "delete from conductors;"
echo "removing leases"
[[ -e /var/lib/dnsmasq/dnsmasq.leases ]] && > /var/lib/dnsmasq/dnsmasq.leases
echo "removing logs"
rm -rf /var/log/libvirt/baremetal_logs/*.log

# clean up dib images only if requested explicitly
CLEAN_DIB_IMAGES=${CLEAN_DIB_IMAGES:-false}

if [ $CLEAN_DIB_IMAGES = "true" ]; then
    rm -rf /httpboot/*
    rm -rf /tftpboot/*
fi

# remove VM disk images
rm -rf /var/lib/libvirt/images/*.qcow2

echo "restarting services"
service libvirtd restart
service ironic-api restart
service ironic-conductor start
service ironic-inspector restart
