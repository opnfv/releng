How to deploy bifrost
=====================

The scripts and playbooks defined on this repo, need to be combined with proper [Bifrost](http://git.openstack.org/cgit/openstack/bifrost) code.

Please follow that steps:

1. Clone bifrost:
```
    git clone https://git.openstack.org/openstack/bifrost /opt/bifrost
```

2. Clone releng:
```
    git clone https://gerrit.opnfv.org/gerrit/releng /opt/releng
```

3. Clone infracloud:
```
    git clone https://git.openstack.org/openstack-infra/puppet-infracloud /opt/puppet-infracloud
```

4. Combine releng scripts and playbooks with bifrost:
```
    cp -R /opt/releng/prototypes/bifrost/* /opt/bifrost/
```

5. Run destroy script if you need to cleanup previous environment:
```
    cd /opt/bifrost
    ./scripts/destroy_env.sh
```

6. Run deployment script to spin up 3 vms with bifrost: jumphost, controller and compute:
```
    cd /opt/bifrost
    ./scripts/test-bifrost-deployment.sh
```
It is likely that the script will show some errors due to timeout. Please ignore the errors, and wait until the vms are completely bootstrapped. To verify it you can check with ironic:
```
    cd /opt/bifrost
    source env-vars
    ironic node-list
```
And wait until all the vms are in **active** Provisioning State.

7. Check the IPs assigned to each of the VMS. You can check it by looking at inventory:
```
    cat /tmp/baremetal.csv
```

8. You can enter into the vms with devuser login/pass:
```
    ssh devuser@192.168.122.2
```
