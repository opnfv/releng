#!/bin/bash
#This script will help keep your jnlp slave connection up and update the slave.jar before connection.
#run this script as root, then start monit.
#Config consists of these 4 lines. Run as root to install and configure monit, then start monit
jenkinshome=""
jenkinsuser=""
slave_name=""
slave_secret=""
connectionstring="java -jar slave.jar -jnlpUrl https://build.opnfv.org/ci/computer/"$slave_name"/slave-agent.jnlp -secret "$slave_secret""
distro="$(tr -s ' \011' '\012' < /etc/issue | head -n 1)"


#tests
if [[ -z $jenkinsuser || -z $jenkinshome ]]; then
  echo "jenkinsuser or home not defined, please edit this file to define it"
  exit 1
fi

if [[ -z $slave_name || -z $slave_secret ]]; then
  echo "slave name or secret not defined, please edit this file to define it"
  exit 1
fi

if [[ -x "/home/$jenkinsuser/jenkins-jnlp-connect.sh" ]]; then
  echo "jenkins-jnlp-connect.sh is in the correct place and is executable"
else
  echo "please make sure this script is called jenkins-jnlp-connect.sh and is executable"
  exit 1
fi

#detect distro
if [[ $distro == Debian || $distro == Ubuntu ]]; then
  monitconfdir="/etc/monit/conf.d/"
elif [[ $distro == Fedora || $distro == CentOS || $distro == Redhat ]]; then
  monitconfdir="/etc/monit.d"
fi

#make pid dir
if ! [ -d /var/run/$jenkinsuser/ ]; then
  mkdir   /var/run/$jenkinsuser/
  chown $jenkinsuser:$jenkinsuser /var/run/$jenkinsuser/
fi

#create pid file
pidfile="/var/run/$jenkinsuser/jenkins_jnlp_pid"
echo $$ > /var/run/$jenkinsuser/jenkins_jnlp_pid
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

makemonit () {
echo "Writing the following as monit config:"
cat << EOF | tee $monitconfdir/jenkins
check process bash with pidfile /var/run/$jenkinsuser/jenkins_jnlp_pid
start program = "/bin/bash -c 'cd /home/$jenkinsuser/; export started_monit=true; /home/$jenkinsuser/jenkins-jnlp-connect.sh' as uid $jenkinsuser and gid $jenkinsuser"
stop program = "/bin/kill \$(/bin/cat /var/run/$jenkinsuser/jenkins_jnlp_pid)"
EOF
}

if [[ -f $monitconfdir/jenkins ]]; then
  #test for diff
  if [[ "$(diff $monitconfdir/jenkins <(echo "\
check process bash with pidfile /var/run/$jenkinsuser/jenkins_jnlp_pid
start program = \"/bin/bash -c 'cd /home/$jenkinsuser/; export started_monit=true; /home/$jenkinsuser/jenkins-jnlp-connect.sh' as uid $jenkinsuser and gid $jenkinsuser\"
stop program = \"/bin/kill \$(/bin/cat /var/run/$jenkinsuser/jenkins_jnlp_pid)\"\
") )" ]]; then
    echo "Updating monit config..."
    makemonit
  fi
else
  makemonit
fi


if [[ $started_monit == "true" ]]; then
  wget --timestamping https://build.opnfv.org/ci/jnlpJars/slave.jar && true
  $connectionstring
else
  echo "you are ready to start monit"
  echo "eg: /etc/init.d/monit start"
  echo "example debug mode if you are having problems:  /usr/bin/monit -Ivv -c /etc/monit.conf "
  exit 0
fi
