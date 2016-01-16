#!/bin/bash
set -x

# log info to console
echo "Starting the deployment on virtual environment using $INSTALLER_TYPE. This could take some time..."
echo "--------------------------------------------------------"
echo

export ISO_URL=file://$BUILD_DIRECTORY/compass.iso
export OS_VERSION=${{COMPASS_OS_VERSION}}
export OPENSTACK_VERSION=${{COMPASS_OPENSTACK_VERSION}}
export CONFDIR=$WORKSPACE/deploy/conf/vm_environment
./deploy.sh --dha $CONFDIR/$DEPLOY_SCENARIO.yml --network $CONFDIR/$NODE_NAME/network.yml
if [ $? -ne 0 ]; then
    echo "depolyment failed!"
    deploy_ret=1
fi

echo
echo "--------------------------------------------------------"
echo "Done!"

ssh_options="-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
sshpass -p root scp 2>/dev/null $ssh_options root@${{INSTALLER_IP}}:/var/ansible/run/openstack_${{COMPASS_OPENSTACK_VERSION}}-opnfv2/ansible.log ./  &> /dev/null

exit $deploy_ret
