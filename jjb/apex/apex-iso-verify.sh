#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Starting the Apex iso verify."
echo "--------------------------------------------------------"
echo

if [ "$BRANCH" == 'master' ]; then
  echo "Skipping Apex iso verify for master branch"
  exit 0
fi

# Must be RPMs/ISO
echo "Downloading latest properties file"

# get the properties file in order to get info regarding artifacts
curl --fail -s -o opnfv.properties http://$GS_URL/latest.properties

# source the file so we get OPNFV vars
source opnfv.properties

if ! rpm -q virt-install > /dev/null; then
  sudo yum -y install virt-install
fi

# define a clean function
rm_apex_iso_verify () {
if sudo virsh list --all | grep apex-iso-verify | grep running; then
    sudo virsh destroy apex-iso-verify
fi
if sudo virsh list --all | grep apex-iso-verify; then
    sudo virsh undefine apex-iso-verify
fi
}

# Make sure a pre-existing iso-verify isn't there
rm_apex_iso_verify

#make sure there is not an existing console log file for the VM
sudo rm -f /var/log/libvirt/qemu/apex-iso-verify-console.log

# run an install from the iso
# This streams a serial console to tcp port 3737 on localhost
sudo virt-install -n apex-iso-verify -r 4096 --vcpus 4 --os-variant=rhel7 \
 --accelerate -v --noautoconsole \
 --disk path=/var/lib/libvirt/images/apex-iso-verify.qcow2,size=30,format=qcow2 \
 -l /tmp/apex-iso/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso \
 --extra-args 'console=ttyS0 console=ttyS0,115200n8 serial inst.ks=file:/iso-verify.ks inst.stage2=hd:LABEL=OPNFV\x20CentOS\x207\x20x86_64:/' \
 --initrd-inject ci/iso-verify.ks \
 --serial file,path=/var/log/libvirt/qemu/apex-iso-verify-console.log

echo "Waiting for install to finish..."
sleep 10
end_time=$(($SECONDS+1500))
while ! [[ `sudo tail -n1 /var/log/libvirt/qemu/apex-iso-verify-console.log` =~ 'Power down' ]]; do
  if [ $SECONDS -gt $end_time ] || ! sudo virsh list --all | grep apex-iso-verify | grep running > /dev/null; then
    sudo cat /var/log/libvirt/qemu/apex-iso-verify-console.log
    sudo virsh list --all
    echo "Error: Failed to find power down message after install"
    exit 1
  fi
  sleep 10
done

sudo cat /var/log/libvirt/qemu/apex-iso-verify-console.log

# clean up
rm_apex_iso_verify

echo
echo "--------------------------------------------------------"
echo "Done!"
