# This is an example of usage of this Tool
# Author: Jose Lausuch (jose.lausuch@ericsson.com)

from InstallerHandler import InstallerHandler

fuel_handler = InstallerHandler(scenario='os-nosdn-nofeature-ha',
                                installer='fuel',
                                installer_ip='10.20.0.2',
                                installer_user='root',
                                installer_pwd='r00tme')

print("Nodes:\n%s\n" % fuel_handler.get_nodes())
print("Controller nodes:\n%s\n" % fuel_handler.get_controller_ips())
print("Compute nodes:\n%s\n" % fuel_handler.get_compute_ips())
print("Deployment info:\n%s\n" % fuel_handler.get_deployment_info())