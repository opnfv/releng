# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 RedHat and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
class opnfv::controller (
  $keystone_rabbit_password,
  $neutron_rabbit_password,
  $nova_rabbit_password,
  $root_mysql_password,
  $keystone_mysql_password,
  $glance_mysql_password,
  $neutron_mysql_password,
  $nova_mysql_password,
  $glance_admin_password,
  $keystone_admin_password,
  $neutron_admin_password,
  $nova_admin_password,
  $keystone_admin_token,
  $ssl_key_file_contents,
  $ssl_cert_file_contents,
  $br_name,
  $controller_public_address = $::fqdn,
  $neutron_subnet_cidr,
  $neutron_subnet_gateway,
  $neutron_subnet_allocation_pools,
  $opnfv_password,
  $opnfv_email = 'opnfvuser@gmail.com',
) {
  class { '::infracloud::controller':
    keystone_rabbit_password         => $keystone_rabbit_password,
    neutron_rabbit_password          => $neutron_rabbit_password,
    nova_rabbit_password             => $nova_rabbit_password,
    root_mysql_password              => $root_mysql_password,
    keystone_mysql_password          => $keystone_mysql_password,
    glance_mysql_password            => $glance_mysql_password,
    neutron_mysql_password           => $neutron_mysql_password,
    nova_mysql_password              => $nova_mysql_password,
    keystone_admin_password          => $keystone_admin_password,
    glance_admin_password            => $glance_admin_password,
    neutron_admin_password           => $neutron_admin_password,
    nova_admin_password              => $nova_admin_password,
    keystone_admin_token             => $keystone_admin_token,
    ssl_key_file_contents            => $ssl_key_file_contents,
    ssl_cert_file_contents           => $ssl_cert_file_contents,
    br_name                          => $br_name,
    controller_public_address        => $controller_public_address,
    neutron_subnet_cidr              => $neutron_subnet_cidr,
    neutron_subnet_gateway           => $neutron_subnet_gateway,
    neutron_subnet_allocation_pools  => $neutron_subnet_allocation_pools,
  }

  # create keystone creds
  keystone_domain { 'opnfv':
    ensure  => present,
    enabled => true,
  }

  keystone_tenant { 'opnfv':
    ensure      => present,
    enabled     => true,
    description => 'OPNFV cloud',
    domain      => 'opnfv',
    require     => Keystone_domain['opnfv'],
  }

  keystone_user { 'opnfv':
    ensure   => present,
    enabled  => true,
    domain   => 'opnfv',
    email    => $opnfv_email,
    password => $opnfv_password,
    require  => Keystone_tenant['opnfv'],
  }

  keystone_role { 'user': ensure => present }

  keystone_user_role { 'opnfv::opnfv@opnfv::opnfv':
    roles => [ 'user', 'admin', ],
  }
}

