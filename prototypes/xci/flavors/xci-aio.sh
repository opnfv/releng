#-------------------------------------------------------------------------------
# XCI Flavor Configuration
#-------------------------------------------------------------------------------
# This is the configuration for xci-aio.
#
# You are free to modify parts of the configuration to fit into your environment.
# But before doing that, please ensure you checked other flavors to see if one
# them can be used instead, saving you some time.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Configure VM Nodes
#-------------------------------------------------------------------------------
export TEST_VM_NUM_NODES=1
export TEST_VM_NODE_NAMES=xciaio
export VM_DOMAIN_TYPE=kvm
export VM_CPU=8
export VM_DISK=80
export VM_MEMORY_SIZE=12288
export VM_DISK_CACHE=unsafe

#-------------------------------------------------------------------------------
# Ansible Files for the Flavor
#-------------------------------------------------------------------------------
XCI_ANSIBLE_PLAYBOOK=$OPNFV_RELENG_PATH/prototypes/xci/file/configure-xci-aio.yml
XCI_ANSIBLE_INVENTORY=$OPNFV_RELENG_PATH/prototypes/xci/file/xci-aio-inventory
XCI_ANSIBLE_VARS=$OPNFV_RELENG_PATH/prototypes/xci/file/xci-aio-vars.yml
