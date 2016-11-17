# This is an example of usage of this Tool
# Author: Jose Lausuch (jose.lausuch@ericsson.com)

from InstallerHandler import InstallerHandler

fuel_handler = InstallerHandler(installer='fuel',
                                installer_ip='10.20.0.2',
                                installer_user='root',
                                installer_pwd='r00tme')
print("Nodes in cluster 1:\n%s\n" %
      fuel_handler.get_nodes(options={'cluster': '1'}))
print("Nodes in cluster 2:\n%s\n" %
      fuel_handler.get_nodes(options={'cluster': '2'}))
print("Nodes:\n%s\n" % fuel_handler.get_nodes())
print("Controller nodes:\n%s\n" % fuel_handler.get_controller_ips())
print("Compute nodes:\n%s\n" % fuel_handler.get_compute_ips())
print("\n%s\n" % fuel_handler.get_deployment_info())
fuel_handler.get_file_from_installer('/root/deploy/dea.yaml', './dea.yaml')
fuel_handler.get_file_from_controller(
    '/etc/neutron/neutron.conf', './neutron.conf')
fuel_handler.get_file_from_controller(
    '/root/openrc', './openrc')
