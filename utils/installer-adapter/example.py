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


'''
$ python example.py

Nodes in cluster 1:
[{'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:2a', 'name': u'Untitled (00:2a)', 'roles': u'controller, opendaylight', 'online': u'1', 'ip': u'10.20.0.3', 'id': u'5'}, {'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:4a', 'name': u'Untitled (00:4a)', 'roles': u'ceph-osd, controller', 'online': u'1', 'ip': u'10.20.0.5', 'id': u'4'}, {'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:5a', 'name': u'Untitled (00:5a)', 'roles': u'ceph-osd, compute', 'online': u'1', 'ip': u'10.20.0.6', 'id': u'3'}, {'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:6a', 'name': u'Untitled (00:6a)', 'roles': u'ceph-osd, compute', 'online': u'1', 'ip': u'10.20.0.7', 'id': u'2'}, {'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:3a', 'name': u'Untitled (00:3a)', 'roles': u'controller, mongo', 'online': u'1', 'ip': u'10.20.0.4', 'id': u'1'}]

Nodes in cluster 2:
[]

Nodes:
[{'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:2a', 'name': u'Untitled (00:2a)', 'roles': u'controller, opendaylight', 'online': u'1', 'ip': u'10.20.0.3', 'id': u'5'}, {'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:4a', 'name': u'Untitled (00:4a)', 'roles': u'ceph-osd, controller', 'online': u'1', 'ip': u'10.20.0.5', 'id': u'4'}, {'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:5a', 'name': u'Untitled (00:5a)', 'roles': u'ceph-osd, compute', 'online': u'1', 'ip': u'10.20.0.6', 'id': u'3'}, {'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:6a', 'name': u'Untitled (00:6a)', 'roles': u'ceph-osd, compute', 'online': u'1', 'ip': u'10.20.0.7', 'id': u'2'}, {'status': u'ready', 'cluster': u'1', 'mac': u'00:25:b5:a0:00:3a', 'name': u'Untitled (00:3a)', 'roles': u'controller, mongo', 'online': u'1', 'ip': u'10.20.0.4', 'id': u'1'}]

Controller nodes:
[u'10.20.0.3', u'10.20.0.5', u'10.20.0.4']

Compute nodes:
[u'10.20.0.6', u'10.20.0.7']


Deployment details:
    Installer:  Fuel
    Scenario:   Unknown
    N.Clusters: 1
    Cluster info:
       ID:          1
       NAME:        opnfv
       STATUS:      operational
       HA:          True
       NUM.NODES:   5
       CONTROLLERS: 3
       COMPUTES:    2
       SDN:         OpenDaylight

id | status | name             | cluster | ip        | mac               | roles                    | pending_roles | online | group_id
---+--------+------------------+---------+-----------+-------------------+--------------------------+---------------+--------+---------
 5 | ready  | Untitled (00:2a) |       1 | 10.20.0.3 | 00:25:b5:a0:00:2a | controller, opendaylight |               |      1 |        1
 4 | ready  | Untitled (00:4a) |       1 | 10.20.0.5 | 00:25:b5:a0:00:4a | ceph-osd, controller     |               |      1 |        1
 3 | ready  | Untitled (00:5a) |       1 | 10.20.0.6 | 00:25:b5:a0:00:5a | ceph-osd, compute        |               |      1 |        1
 2 | ready  | Untitled (00:6a) |       1 | 10.20.0.7 | 00:25:b5:a0:00:6a | ceph-osd, compute        |               |      1 |        1
 1 | ready  | Untitled (00:3a) |       1 | 10.20.0.4 | 00:25:b5:a0:00:3a | controller, mongo        |               |      1 |        1

'''