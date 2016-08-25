class opnfv::compute (
  $nova_rabbit_password,
  $neutron_rabbit_password,
  $neutron_admin_password,
  $ssl_cert_file_contents,
  $ssl_key_file_contents,
  $br_name,
  $controller_public_address,
  $virt_type = 'kvm',
) {
  # disable selinux if needed
  if $::osfamily == 'RedHat' {
    class { 'selinux':
      mode   => 'permissive',
      before => Class['::infracloud::compute'],
    }
  }

  class { '::infracloud::compute':
    nova_rabbit_password          => $nova_rabbit_password,
    neutron_rabbit_password       => $neutron_rabbit_password,
    neutron_admin_password        => $neutron_admin_password,
    ssl_cert_file_contents        => $ssl_cert_file_contents,
    ssl_key_file_contents         => $ssl_key_file_contents,
    br_name                       => $br_name,
    controller_public_address     => $controller_public_address,
    virt_type                     => $virt_type,
  }

}

