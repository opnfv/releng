# This is an example of usage of this Tool
# Author: Jose Lausuch (jose.lausuch@ericsson.com)

from opnfv.deployment import factory

print("########## APEX ##########")
handler = factory.Factory.get_handler('apex',
                                      '192.168.122.135',
                                      'stack',
                                      pkey_file='/root/.ssh/id_rsa')


installer_node = handler.get_installer_node()
print("Hello, I am node '%s'" % installer_node.run_cmd('hostname'))
installer_node.get_file('/home/stack/overcloudrc', './overcloudrc')

nodes = handler.get_nodes()
for node in nodes:
    print("Hello, I am node '%s' and my ip is %s." %
          (node.run_cmd('hostname'), node.ip))

print(handler.get_deployment_info())


print("########## FUEL ##########")
# NOTE: If you get traces containing <paramiko.ecdsakey.ECDSAKey object [...]>
# make sure 10.20.0.2 is not already in ~/.ssh/known_hosts with another sig
handler = factory.Factory.get_handler('fuel',
                                      '10.20.0.2',
                                      'ubuntu',
                                      pkey_file='/var/lib/opnfv/mcp.rsa')

print(handler.get_deployment_info())

print("List of nodes in cluster")
nodes = handler.get_nodes()
for node in nodes:
    print(node)


print("########## COMPASS ##########")
handler = factory.Factory.get_handler('compass',
                                      '192.168.200.2',
                                      'root',
                                      installer_pwd='root')

print(handler.get_deployment_status())
print(handler.get_deployment_info())
print('Details of each node:')
nodes = handler.nodes
for node in nodes:
    print(node)
