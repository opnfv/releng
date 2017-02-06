# This is an example of usage of this Tool
# Author: Jose Lausuch (jose.lausuch@ericsson.com)

from opnfv.deployment.apex import adapter

apex_handler = adapter.ApexAdapter(installer_ip='192.168.122.135',
                                   installer_user='stack',
                                   pkey_file='/root/.ssh/id_rsa')

print("\n%s\n" % apex_handler.get_deployment_info())

for node in apex_handler.get_nodes():
    print("Doing operations on node: %s" % node.run_cmd('hostname'))
    print("Node info: %s" % node)
    node.put_file('/etc/resolv.conf', '/home/heat-admin/test.txt')
    node.get_file('/home/heat-admin/test.txt', './test.txt')
