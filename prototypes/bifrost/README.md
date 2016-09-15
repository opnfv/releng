=====================
How to deploy bifrost
=====================
The scripts and playbooks defined on this repo, need to be combined with proper `Bifrost <http://git.openstack.org/cgit/openstack/bifrost>`_ code.

Please follow that steps:

1. Clone bifrost::

    sudo git clone https://git.openstack.org/openstack/bifrost /opt/bifrost

2. Clone releng::

    sudo git clone https://gerrit.opnfv.org/gerrit/releng /opt/releng

3. Clone infracloud::

    sudo git clone https://git.openstack.org/openstack-infra/puppet-infracloud /opt/puppet-infracloud

4. Combine releng scripts and playbooks with bifrost::

    sudo cp -R /opt/releng/prototypes/bifrost/* /opt/bifrost/

5. If you are on a RHEL/CentOS box, ensure that selinux is disabled

6. Run destroy script if you need to cleanup previous environment::

    cd /opt/bifrost
    sudo ./scripts/destroy-env.sh

7. Run deployment script to spin up 3 vms with bifrost: jumphost, controller and compute::

    cd /opt/bifrost
    sudo ./scripts/test-bifrost-deployment.sh

It is likely that the script will show some errors due to timeout. Please ignore the errors, and wait until the vms are completely bootstrapped. To verify it you can check with ironic::

    cd /opt/bifrost
    source env-vars
    ironic node-list

And wait until all the vms are in **active** Provisioning State.

8. Check the IPs assigned to each of the VMS. You can check it by looking at inventory:

    cat /tmp/baremetal.csv

9. You can enter into the vms with devuser login/pass:

    ssh devuser@192.168.122.2
