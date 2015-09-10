#!/bin/bash

PUBLIC_GW='172.30.10.1'
NET_RECONF_LOG=/var/log/net_reconf.log
NETWORK_CFG_DIR=/etc/sysconfig/network-scripts

_me=$(readlink -e ${BASH_SOURCE[0]})
dir_here="${_me%/*}"

# When more installers will come we create more config directories
FUEL_CFG_DIR=${dir_here}/net_cfg/fuel
FOREMAN_CFG_DIR=${dir_here}/net_cfg/foreman

function is_gw_reachable()
{
    if ping -c 1 $PUBLIC_GW; then
        echo "OK. Gateway is Reachable."
        exit 0
    fi  
}

date > $NET_RECONF_LOG
is_gw_reachable
# for loop may be updated to iterate over more directories 
for CFG_DIR in $FUEL_CFG_DIR $FOREMAN_CFG_DIR; do
    rm -rvf $NETWORK_CFG_DIR/ifcfg-*
    cp -v $CFG_DIR/ifcfg-* $NETWORK_CFG_DIR/
    /etc/init.d/network restart
    is_gw_reachable
done 2>&1 >> $NET_RECONF_LOG

echo "ERROR: Cannot ping default GW" >> $NET_RECONF_LOG
