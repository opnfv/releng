#!/bin/bash
set +e
IMAGES=/var/lib/libvirt/images

echo "------ VM List ------"
virsh list

echo "------ Destroy Bootstrap ------"
VM=$(virsh list --name |grep bootstrap)
if [ "z$VM" = "z" ]
    then "echo NO Bootstrap VM"
    else {{
        virsh destroy $VM
        virsh undefine $VM
        virsh vol-delete --pool default $IMAGES/$VM.img
    }}
fi

echo "------ Destroy MAAS ------"
VM=$(virsh list --name |grep maas)
if [ "z$VM" = "z" ]
    then "echo NO MAAS VM"
    else {{
        virsh destroy $VM
        virsh undefine $VM
        virsh vol-delete --pool default $IMAGES/$VM-root.img
        virsh vol-delete --pool default $IMAGES/$VM-seed.img
    }}
fi
