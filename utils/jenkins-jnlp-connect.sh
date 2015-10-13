#!/bin/bash
#This script will help keep your jnlp slave connection up and update the slave.jar before connection.
#Config consists of these 4 lines. Run as root to install and configure monit, then start monit
jenkinshome="/home/jenkins-ci"
jenkinsuser="jenkins-ci"
slave_name=""
slave_secret=""
connectionstring="slave.jar -jnlpUrl https://build.opnfv.org/ci/computer/"$slave_name"/slave-agent.jnlp -secret "$secret""

if [[ -z $jenkinsuser || -z $jenkinshome ]]; then
  echo "jenkinsuser or home not defined, please edit this file to define it"
  exit 1
fi

if [[ -z $slave_name || -z $slave_secret ]]; then
  echo "slave name or secret not defined, please edit this file to define it"
  exit 1
fi

#detect distro
distro="$(tr -s ' \011' '\012' < /etc/issue | head -n 1)"
if [[ $distro == Debian || $distro == Ubuntu ]]; then
monitconfdir="/etc/monit.d"
elif [[ $distro == Fedora || $distro == CentOS || $distro == Redhat ]]; then 
monitconfdir="/etc/monit/conf.d/"
fi

#make pid dir
if ! [ -d /var/run/$jenkinsuser/ ]; then
  mkdir   /var/run/$jenkinsuser/
  chown $jenkinsuser:$jenkinsuser /var/run/$jenkinsuser/
fi

#create pid file
pidfile="/var/run/jenkins/jenkins_jnlp_pid"
echo $$ > /var/run/jenkins/jenkins_jnlp_pid
trap 'rm -f "$pidfile"; exit' EXIT SIGQUIT SIGINT SIGSTOP SIGTERM

#test firewall
echo "testing that the firewall is open for us at build.opnfv.org"
if [[ "$(nc -w 4 build.opnfv.org 57387; echo $?) != 0" ]]; then
  :
else
  echo "LF firewall not open, please send a report to helpdesk"
  exit 1
fi

#intall monit if needed
if [ $(which monit) ]; then
  echo "monit installed"
else

#apt-get install monit or yum install monit
  if [ -n "$(command -v yum)" ]; then
    echo "please install monit; eg: yum -y install monit"
    exit 1
  elif [ -n "$(command -v apt-get)" ]; then
    echo "please install monit  eg: apt-get install -y monit"
    exit 1
  else
    echo "system not supported"
    exit 1
  fi
fi

#create monit conf file if needed
if [[ -f $monitconfdir/jenkins ]]; then
  :
else
cat << EOF > $monitconfdir/jenkins
check process bash with pidfile /var/run/$jenkinsuser/pid_file
start program = "/bin/bash -c 'cd /home/$jenkinsuser/; export started_monit=true; /home/$jenkinsuser/Connect_OPNFV_Slave'" as uid $jenkinsuser and gid $jenkinsuser
stop program = "/bin/kill $(/bin/cat /var/run/"$jenkinsuser"/pid_file)"
EOF
fi

if [[ $started_monit == "true" ]]; then

  if [[ $(whoami) == "$jenkinsuser" ]]; then
    #grab new slave.jar if avaliable
    wget --timestamping https://build.opnfv.org/ci/jnlpJars/slave.jar && true
    #Start slave
    java -jar "$connectionstring"
  else
     echo "please run this program as "$jenkinsuser""
  exit 1
  fi

else
  echo "you are ready to start monit"
  echo "example debug mode:  /usr/bin/monit -Ivv -c /etc/monit.conf "
  exit 0
fi
