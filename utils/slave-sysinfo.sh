#!/bin/bash
echo "" 
echo ": "
$(printf "\n %s %s" )

echo ""
echo "Date: "
$(printf "\n %s %s" date)

echo ""
echo "Uptime: "
$(printf "\n %s %s" uptime)

echo ""
echo "Current user is : "
$(printf "\n %s %s" whoami)

echo ""
echo "Checking for passwordless sudo: "
$(printf "\n %s %s" sudo -n true)

echo ""
echo "Current system is : "
$(printf "\n %s %s" uname -a)

echo ""
echo "Number of cores: "
$(printf "\n %s %s" getconf _NPROCESSORS_ONLN)

echo ""
echo "Proccessor Speed: "
$(printf "\n %s %s" cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_max_freq)

echo ""
echo "Memory: "
$(printf "\n %s %s" free -m)


echo ""
echo "Current connected devices are : "
$(printf "\n %s %s" arp -a)


echo ""
echo "Current IP configuration is : "
$(printf "\n %s %s" ifconfig)
  
echo ""
echo "Done."



