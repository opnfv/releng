===============================
How to deploy puppet-infracloud
===============================
The manifest and mmodules defined on this repo will deploy an OpenStack cloud based on `Infra Cloud <http://docs.openstack.org/infra/system-config/infra-cloud.html>`_ project.

Once all the hardware is provisioned, enter in controller and compute nodes and follow these steps:

1. Clone releng::

    git clone https://gerrit.opnfv.org/gerrit/releng /opt/releng

2. Copy hiera to the right place::

    cp /opt/releng/prototypes/puppet-infracloud/hiera/common.yaml /var/lib/hiera/    

3. Install modules::

    cd /opt/releng/prototypes/puppet-infracloud
    ./install_modules.sh

4. Apply the infracloud manifest::

    cd /opt/releng/prototypes/puppet-infracloud
    puppet apply --manifests/site.pp --modulepath=/etc/puppet/modules:/opt/releng/prototypes/puppet-infracloud/modules

5. Once you finish this operation on controller and compute nodes, you will have a functional OpenStack cloud.

In jumphost, follow that steps:

1. Clone releng::

    git clone https://gerrit.opnfv.org/gerrit/releng /opt/releng

2. Create OpenStack clouds config directory:

    mkdir -p /root/.config/openstack

3. Copy credentials file::

    cp /opt/releng/prototypes/puppet-infracloud/creds/clouds.yaml /root/.config/openstack/

4. Install openstack-client:

    pip install python-openstackclient

5. Export the desired cloud::

    export OS_CLOUD=opnfv

6. Start using it::

    openstack server list
