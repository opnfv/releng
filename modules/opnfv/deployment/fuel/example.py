# This is an example of usage of this Tool
# Author: Jose Lausuch (jose.lausuch@ericsson.com)

from opnfv.deployment.fuel import adapter

fuel_handler = adapter.FuelAdapter(installer_ip='10.20.0.2',
                                   installer_user='root',
                                   installer_pwd='r00tme')
print("\n%s\n" % fuel_handler.get_deployment_info())

for node in fuel_handler.get_nodes():
    if node.is_controller():
        print("Node info: %s" % node)
        node.put_file('/etc/resolv.conf', '/root/test.txt')
        node.get_file('/root/test.txt', './test.txt')
        break
