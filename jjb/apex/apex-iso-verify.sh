#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# log info to console
echo "Starting the Apex iso verify."
echo "--------------------------------------------------------"
echo

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

# run an install from the iso
# This streams a serial console to tcp port 3737 on localhost
sudo virt-install -n apex-iso-verify -r 4096 --vcpus 4 --os-variant=rhel7 \
 --accelerate -v --noautoconsole --nographics \
 --disk path=/var/lib/libvirt/images/apex-iso-verify.qcow2,size=30,format=qcow2 \
 -l $BUILD_DIRECTORY/release/OPNFV-CentOS-7-x86_64-$OPNFV_ARTIFACT_VERSION.iso \
 --extra-args 'console=ttyS0 console=ttyS0,115200n8 serial inst.ks=file:/iso-verify.ks inst.stage2=hd:LABEL=OPNFV\x20CentOS\x207\x20x86_64:/' \
 --initrd-inject $BUILD_DIRECTORY/../ci/iso-verify.ks \
 --serial tcp,host=:3737,protocol=raw

# Attach to tcpport 3737 and echo the output to stdout
# watch for a 5 min time out, a power off message or a tcp disconnect
python << EOP
#!/usr/bin/env python

import sys
import socket
from time import sleep
from time import time


TCP_IP = '127.0.0.1'
TCP_PORT = 3737
BUFFER_SIZE = 1024

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
except Exception, e:
    print "Failed to connect to the iso-verofy vm's serial console"
    print "this probably means that the VM failed to start"
    raise e

activity = time()
data = s.recv(BUFFER_SIZE)
last_data = data
while time() - activity < 300:
    try:
        if data != last_data:
            activity = time()
        last_data = data
        data = s.recv(BUFFER_SIZE)
        sys.stdout.write(data)
        if 'Powering off' in data:
            break
        sleep(.5)
    except socket.error, e:
        # for now assuming that the connection was closed
        # which is good, means the vm finished installing
        # printing the error output just in case we need to debug
        print "VM console connection lost: %s" % msg
        break
s.close()

if time() - activity > 300:
    print "failing due to console inactivity"
    exit(1)
else:
    print "Success!"
EOP

# save the python return code for after cleanup
python_rc=$?

# clean up
rm_apex_iso_verify

# Exit with the RC of the Python job
exit $python_rc

echo
echo "--------------------------------------------------------"
echo "Done!"
