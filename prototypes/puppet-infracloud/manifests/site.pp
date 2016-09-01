# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 RedHat and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
node 'controller00.opnfvlocal' {
  $group = 'infracloud'
  class { 'opnfv::server':
    iptables_public_tcp_ports => [80,5000,5671,8774,9292,9696,35357], # logs,keystone,rabbit,nova,glance,neutron,keystone
    sysadmins                 => hiera('sysadmins', []),
    enable_unbound            => false,
    purge_apt_sources         => false,
  }
  class { 'opnfv::controller':
    keystone_rabbit_password         => hiera('keystone_rabbit_password'),
    neutron_rabbit_password          => hiera('neutron_rabbit_password'),
    nova_rabbit_password             => hiera('nova_rabbit_password'),
    root_mysql_password              => hiera('infracloud_mysql_password'),
    keystone_mysql_password          => hiera('keystone_mysql_password'),
    glance_mysql_password            => hiera('glance_mysql_password'),
    neutron_mysql_password           => hiera('neutron_mysql_password'),
    nova_mysql_password              => hiera('nova_mysql_password'),
    keystone_admin_password          => hiera('keystone_admin_password'),
    glance_admin_password            => hiera('glance_admin_password'),
    neutron_admin_password           => hiera('neutron_admin_password'),
    nova_admin_password              => hiera('nova_admin_password'),
    keystone_admin_token             => hiera('keystone_admin_token'),
    ssl_key_file_contents            => hiera('ssl_key_file_contents'),
    ssl_cert_file_contents           => hiera('ssl_cert_file_contents'),
    br_name                          => hiera('bridge_name'),
    controller_public_address        => $::fqdn,
    neutron_subnet_cidr              => '192.168.122.0/24',
    neutron_subnet_gateway           => '192.168.122.1',
    neutron_subnet_allocation_pools  => [
                                          'start=192.168.122.50,end=192.168.122.254',
                                        ],
    opnfv_password                   => hiera('opnfv_password'),
  }
}

node 'compute00.opnfvlocal' {
  $group = 'infracloud'
  class { 'opnfv::server':
    sysadmins                 => hiera('sysadmins', []),
    enable_unbound            => false,
    purge_apt_sources         => false,
  }

  class { 'opnfv::compute':
    nova_rabbit_password             => hiera('nova_rabbit_password'),
    neutron_rabbit_password          => hiera('neutron_rabbit_password'),
    neutron_admin_password           => hiera('neutron_admin_password'),
    ssl_cert_file_contents           => hiera('ssl_cert_file_contents'),
    ssl_key_file_contents            => hiera('ssl_key_file_contents'),
    br_name                          => hiera('bridge_name'),
    controller_public_address        => 'controller00.opnfvlocal',
    virt_type                        => 'qemu',
  }
}

node 'jumphost.opnfvlocal' {
  class { 'opnfv::server':
    sysadmins                 => hiera('sysadmins', []),
    enable_unbound            => false,
    purge_apt_sources         => false,
  }
}
