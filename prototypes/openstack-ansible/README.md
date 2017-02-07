===============================
How to deploy OpenStack-Ansible
===============================
The script and playbooks defined on this repo will deploy an OpenStack cloud based on OpenStack-Ansible.
It needs to be combined with Bifrost. You need use Bifrost to provide six VMs. How to use the Bifrost you can read the document </opt/releng/prototypes/bifrost/README.md>.

After provisioning six VMs please follow that steps:

1.Run the script to deploy OpenStack
  cd /opt/releng/prototypes/openstack-ansible/scripts/
  sudo ./osa_deploy.sh
It will take a lot of time. When printing the message "setup openstack successfully" in screen finally, it means that you have deploy successfully.

2.To verify the OpenStack operation
  2.1 enter in controller
      ssh 192.168.122.3
  2.2 enter the lxc
      lxcname=$(lxc-ls | grep utility)
      lxc-attach -n $lxcname
  2.3 verify the OpenStack API
      source /root/openrc
      openstack user list
this will show as following:
+----------------------------------+--------------------+
| ID                               | Name               |
+----------------------------------+--------------------+
| 056f8fe41336435991fd80872731cada | aodh               |
| 308f6436e68f40b49d3b8e7ce5c5be1e | glance             |
| 351b71b43a66412d83f9b3cd75485875 | nova               |
| 511129e053394aea825cce13b9f28504 | ceilometer         |
| 5596f71319d44c8991fdc65f3927b62e | gnocchi            |
| 586f49e3398a4c47a2f6fe50135d4941 | stack_domain_admin |
| 601b329e6b1d427f9a1e05ed28753497 | heat               |
| 67fe383b94964a4781345fbcc30ae434 | cinder             |
| 729bb08351264d729506dad84ed3ccf0 | admin              |
| 9f2beb2b270940048fe6844f0b16281e | neutron            |
| fa68f86dd1de4ddbbb7415b4d9a54121 | keystone           |
+----------------------------------+--------------------+
