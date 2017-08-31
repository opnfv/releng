#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

#This will put a bunch of files in the pwd. you have been warned.
#Counts how long slaves have been online or offline


#Yes I know about jq 
curlcommand() {
curl -s "https://build.opnfv.org/ci/computer/api/json?tree=computer\[displayName,offline\]" \
    | awk -v k=":" '{n=split($0,a,","); for (i=1; i<=n; i++) print a[i]}' \
    | grep -v "_class" \
    | awk 'NR%2{printf "%s ",$0;next;}1'  \
    | awk -F":" '{print $2,$3}' \
    | awk '{print $1,$3}' \
    | sed s,\},,g \
    | sed s,],,g \
    | sed s,\",,g
}

if [ -f podoutput-current ]; then
  cp podoutput-current podoutput-lastiteration
fi

curlcommand > podoutput-current

declare -A slavescurrent slaveslastiteration

while read -r name status ; do
            slavescurrent["$name"]="$status"
done < <(cat podoutput-current)

while read -r name status ; do
            slaveslastiteration["$name"]=$status
done < <(cat podoutput-lastiteration)

main () {
for slavename in "${!slavescurrent[@]}"; do 
    #Slave is online. Mark it down.
    if [ "${slavescurrent[$slavename]}" == "false" ]; then

        if  [ -f "$slavename"-offline ]; then
            echo "removing offline status from $slavename slave was offline for $(cat "$slavename"-offline ) iterations"
            rm "$slavename"-offline
        fi

        if  ! [ -f "$slavename"-online ]; then 
            echo "1" > "$slavename"-online
        elif [ -f "$slavename"-online ]; then 
            #read and increment slavename
            read -r -d $'\x04' var < "$slavename"-online
            ((var++))
            echo -n "ONLINE $slavename "
            echo "for $var iterations"
            echo "$var" > "$slavename"-online
        fi
    fi

    #went offline since last iteration.
    if [ "${slavescurrent[$slavename]}" == "false" ] && [ "${slaveslastiteration[$slavename]}" == "true" ];  then
        echo "JUST WENT OFFLINE $slavename "
        if  [ -f "$slavename"-online ]; then
            echo "removing online status from $slavename. slave was online for $(cat "$slavename"-online ) iterations"
            rm "$slavename"-online
        fi

    fi
    
    #slave is offline
    if [ "${slavescurrent[$slavename]}" == "true" ]; then
        if  ! [ -f "$slavename"-offline ]; then
            echo "1" > "$slavename"-offline
        fi

        if [ -f "$slavename"-offline ]; then 
            #read and increment slavename
            read -r -d $'\x04' var < "$slavename"-offline
            ((var++))
            echo "$var" > "$slavename"-offline
                if  [ "$var" -gt "30" ]; then
                    echo "OFFLINE FOR $var ITERATIONS REMOVE $slavename "
                else
                    echo "OFFLINE $slavename FOR $var ITERATIONS "
                fi
        fi
    fi

done
}

main
