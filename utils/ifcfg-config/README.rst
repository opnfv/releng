Description
-----------

When *lab-reconfig* script modify network for nodes,
we need to be able to connect to public IP of Installer host.
So network config in ``/etc/sysconfig/network-script/`` has to be modified accordingly.

For Fuel it configurues 1st interface as a public and for foreman 3rd.

Usage
-----

Copy file ``swap_ifcfg.sh`` and directory ``net_cfg`` into:
``/usr/lib/systemd/scripts/``

Copy file ``swap_ifcfg.service`` to:
``/usr/lib/systemd/system/``

in order to make it run during boot do:
``systemctl enable swap_ifcfg.service``
