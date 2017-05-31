#!/bin/bash
# SPDX-license-identifier: Apache-2.0
##############################################################################
# Copyright (c) 2016 Linux Foundation and others.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

#Monit setup script for opnfv jnlp slave connections

test_firewall() {
    echo "testing that the firewall is open for us at build.opnfv.org"
    test=$(echo "blah"| nc -w 4 build.opnfv.org 57387 > /dev/null 2>&1; echo $?)
    if [[ $test == 0 ]]; then
        echo "Firewall is open for us at build.opnfv.org"
        exit 0
    else
        cat << EOF
LF firewall not open, please send a report to helpdesk with your gpg key attached, or better yet upload it to the key servers. (I should be able to find it with gpg --search-keys your@company.email.com
opnfv-helpdesk@rt.linuxfoundation.org
Jenkins Home: $jenkinshome
Jenkins User: $jenkinsuser
Slave Name: $slave_name
IP Address: $(curl -s http://icanhazip.com)
EOF
        exit 1
    fi
}

main () {
    #tests
    if [[ -z $jenkinsuser || -z $jenkinshome ]]; then
        echo "jenkinsuser or home not defined, please edit this file to define it"
        exit 1
    fi

    if [[ $(pwd) != "$jenkinshome" ]]; then
        echo "This script needs to be run from the jenkins users home dir"
        exit 1
    fi

    if [[ -z $slave_name || -z $slave_secret ]]; then
        echo "slave name or secret not defined, please edit this file to define it"
        exit 1
    fi

    if [[ $(whoami) != "root" && $(whoami) != "$jenkinsuser"  ]]; then
        echo "This script must be run as user root or jenkins user"
        exit 1
    fi

    if [[ $(whoami) != "root" ]]; then
      if sudo -l | grep "requiretty"; then
        echo "please comment out Defaults requiretty from /etc/sudoers"
        exit 1
      fi
    fi

    #make pid dir
    pidfile="/var/run/$jenkinsuser/jenkins_jnlp_pid"
    if ! [ -d /var/run/$jenkinsuser/ ]; then
        sudo mkdir /var/run/$jenkinsuser/
        sudo chown $jenkinsuser:$jenkinsuser /var/run/$jenkinsuser/
    fi

    if [[ $skip_monit != true ]]; then
        #check for monit
        if [ $(which monit) ]; then
            echo "monit installed"
        else
            if [ -n "$(command -v yum)" ]; then
                echo "please install monit; eg: yum -y install monit"
                exit 1
            elif [ -n "$(command -v apt-get)" ]; then
                echo "please install monit; eg: apt-get install -y monit"
                exit 1
            else
                echo "system not supported plese contact help desk"
                exit 1
            fi
        fi

        if [ -d /etc/monit/conf.d ]; then
            monitconfdir="/etc/monit/conf.d/"
        elif [ -d /etc/monit.d ]; then
            monitconfdir="/etc/monit.d"
        else
            echo "Could not determine the location of the monit configuration file."
            echo "Make sure monit is installed."
            exit 1
        fi

        chown=$(type -p chown)
        mkdir=$(type -p mkdir)

        makemonit () {
            echo "Writing the following as monit config:"
        cat << EOF | tee $monitconfdir/jenkins
check directory jenkins_piddir path /var/run/$jenkinsuser
if does not exist then exec "$mkdir -p /var/run/$jenkinsuser"
if failed uid $jenkinsuser then exec "$chown $jenkinsuser /var/run/$jenkinsuser"
if failed gid $jenkinsuser then exec "$chown :$jenkinsuser /var/run/$jenkinsuser"

check process jenkins with pidfile /var/run/$jenkinsuser/jenkins_jnlp_pid
start program = "/usr/bin/sudo -u $jenkinsuser /bin/bash -c 'cd $jenkinshome; export started_monit=true; $0 $@' with timeout 60 seconds"
stop program = "/bin/bash -c '/bin/kill \$(/bin/cat /var/run/$jenkinsuser/jenkins_jnlp_pid)'"
depends on jenkins_piddir
EOF
        }

        if [[ -f $monitconfdir/jenkins ]]; then
            #test for diff
            if [[ "$(diff $monitconfdir/jenkins <(echo "\
check directory jenkins_piddir path /var/run/$jenkinsuser
if does not exist then exec \"$mkdir -p /var/run/$jenkinsuser\"
if failed uid $jenkinsuser then exec \"$chown $jenkinsuser /var/run/$jenkinsuser\"
if failed gid $jenkinsuser then exec \"$chown :$jenkinsuser /var/run/$jenkinsuser\"

check process jenkins with pidfile /var/run/$jenkinsuser/jenkins_jnlp_pid
start program = \"/usr/bin/sudo -u $jenkinsuser /bin/bash -c 'cd $jenkinshome; export started_monit=true; $0 $@' with timeout 60 seconds\"
stop program = \"/bin/bash -c '/bin/kill \$(/bin/cat /var/run/$jenkinsuser/jenkins_jnlp_pid)'\"
depends on jenkins_piddir\
") )" ]]; then
                echo "Updating monit config..."
                makemonit $@
            fi
        else
            makemonit $@
        fi
    fi

    if [[ $started_monit == "true" ]]; then
        wget --timestamping https://build.opnfv.org/ci/jnlpJars/slave.jar && true
        chown $jenkinsuser:$jenkinsuser slave.jar

        if [[ -f /var/run/$jenkinsuser/jenkins_jnlp_pid ]]; then
            echo "pid file found"
            if ! kill -0 "$(/bin/cat /var/run/$jenkinsuser/jenkins_jnlp_pid)"; then
                echo "no java process running cleaning up pid file"
                rm -f /var/run/$jenkinsuser/jenkins_jnlp_pid;
            else
                echo "java connection process found and running already running quitting."
                exit 1
            fi
        fi

        if [[ $run_in_foreground == true ]]; then
            $connectionstring
        else
            exec $connectionstring &
            echo $! > /var/run/$jenkinsuser/jenkins_jnlp_pid
        fi
    else
        echo "you are ready to start monit"
        echo "eg: service monit start"
        echo "example debug mode if you are having problems:  /usr/bin/monit -Ivv -c /etc/monit.conf "
        exit 0
    fi
}

usage() {
    cat << EOF

**this file must be copied to the jenkins home directory to work**
jenkins-jnlp-connect.sh configures monit to keep slave connection up
Checks for new versions of slave.jar
run as root to create pid directory and create monit config.
can be run as root additional times if you change variables and need to update monit config.
after running as root you should see "you are ready to start monit"

usage: $0 [OPTIONS]
 -h  show this message
 -j  set jenkins home
 -u  set jenkins user
 -n  set slave name
 -s  set secret key
 -t  test the connection string by connecting without monit
 -f  test firewall

Example: $0 -j /home/jenkins -u jenkins -n lab1 -s 727fdefoofoofoofoofoofoofof800
note: a trailing slash on -j /home/jenkins will break the script
EOF

    exit 1
}

if [[ -z "$@" ]]; then
    usage
fi

while getopts "j:u:n:s:htf" OPTION
do
    case $OPTION in
        j ) jenkinshome="$OPTARG" ;;
        u ) jenkinsuser="$OPTARG" ;;
        n ) slave_name="$OPTARG" ;;
        s ) slave_secret="$OPTARG";;
        h ) usage ;;
        t ) started_monit=true
            skip_monit=true
            run_in_foreground=true ;;
        f ) test_firewall ;;
        \? ) echo "Unknown option: -$OPTARG" >&2; exit 1;;
    esac
done

connectionstring="java -jar slave.jar -jnlpUrl https://build.opnfv.org/ci/computer/"$slave_name"/slave-agent.jnlp -secret "$slave_secret" -noCertificateCheck "

main "$@"
