#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

#Counts how long slaves have been online or offline
#exec 2>/dev/null

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

curlcommand > /tmp/podoutput-current

declare -A slavescurrent

while read -r name status ; do
            slavescurrent["$name"]="$status"
done < <(cat /tmp/podoutput-current)

#haste bin stopped allowing post :(
#files=(*online)
#for ((i=0; i<${#files[@]}; i+=9)); do
#./eplot -d -r [-1:74][-1:30] -m    ${files[i]} ${files[i+1]} ${files[i+2]} ${files[i+3]} ${files[i+4]} ${files[i+5]}  ${files[i+6]} ${files[i+7]} ${files[i+8]} ${files[i+9]}
#done  | ./haste.bash
##
main () {

for slavename in "${!slavescurrent[@]}"; do

  #Slave is online. Mark it down.
    if [ "${slavescurrent[$slavename]}" == "false" ]; then

      if  ! [ -f /tmp/"$slavename"-online ]; then
        echo "1" > /tmp/"$slavename"-online
                echo "new online slave file created $slavename ${slavescurrent[$slavename]} up for 1 iterations"
          fi

                #read and increment slavename
                var="$(cat /tmp/"$slavename"-online |tail -n 1)"
                if [[ "$var" == "0" ]]; then
                    echo "slave $slavename ${slavescurrent[$slavename]} back up for $var iterations"
                fi
                ((var++))
                echo "$var" >> /tmp/"$slavename"-online
                unset var
                echo "$slavename up $(cat /tmp/$slavename-online | tail -n 10 | xargs)"

    fi

    #slave is offline remove all points
    if [ "${slavescurrent[$slavename]}" == "true" ]; then
      if  ! [ -f /tmp/"$slavename"-online ]; then
        echo "0" > /tmp/"$slavename"-online
                echo "new offline slave file created $slavename ${slavescurrent[$slavename]} up for 0 iterations"

          fi
          var="$(cat /tmp/"$slavename"-online |tail -n 1)"

            if [[ "$var" != "0" ]]; then
                    echo "slave $slavename ${slavescurrent[$slavename]} was up for $var iterations"
                echo "slave $slavename ${slavescurrent[$slavename]} has gone offline, was $var iterations now reset to 0"
            fi

        echo "0" >> /tmp/"$slavename"-online
            echo "$slavename down $(cat /tmp/$slavename-online | tail -n 10 | xargs)"
            unset var

    fi


done
}

main | sort | column -t
