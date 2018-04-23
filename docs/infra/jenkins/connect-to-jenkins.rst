.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. (c) Open Platform for NFV Project, Inc. and its contributors

.. _connect-to-jenkins:

================================================
Connecting OPNFV Community Labs to OPNFV Jenkins
================================================

.. contents:: Table of Contents
   :backlinks: none

Abstract
========

This document describes how to connect resources (servers) located in Linux Foundation (LF) lab
and labs provided by the OPNFV Community to OPNFV Jenkins.

License
=======
Connecting OPNFV Community Labs to OPNFV Jenkins (c) by Fatih Degirmenci (Ericsson AB) and others.

Connecting OPNFV Labs to OPNFV Jenkins document is licensed under a Creative Commons
Attribution 4.0 International License.

You should have received a copy of the license along with this. If not, see <http://creativecommons.org/licenses/by/4.0/>.


Version History
===============

+------------+-------------+------------------+---------------------------------------+
| **Date**   | **Version** | **Author**       | **Comment**                           |
|            |             |                  |                                       |
+------------+-------------+------------------+---------------------------------------+
| 2015-05-05 | 0.1.0       | Fatih Degirmenci | First draft                           |
|            |             |                  |                                       |
+------------+-------------+------------------+---------------------------------------+
| 2015-09-25 | 1.0.0       | Fatih Degirmenci | Instructions for the                  |
|            |             |                  | Arno SR1 release                      |
+------------+-------------+------------------+---------------------------------------+
| 2016-01-25 | 1.1.0       | Jun Li           | Change the format for                 |
|            |             |                  | new doc toolchain                     |
+------------+-------------+------------------+---------------------------------------+
| 2016-01-27 | 1.2.0       | Fatih Degirmenci | Instructions for the                  |
|            |             |                  | Brahmaputra release                   |
+------------+-------------+------------------+---------------------------------------+
| 2016-05-25 | 1.3.0       | Julien           | Add an additional step after step9 to |
|            |             |                  | output the correct monit config file  |
+------------+-------------+------------------+---------------------------------------+

Jenkins
=======

Jenkins is an extensible open source Continuous Integration (CI) server. [1]

Linux Foundation (LF) hosts and operates `OPNFV Jenkins <https://build.opnfv.org/ci/>`_.

Jenkins Slaves
==============

**Slaves** are computers that are set up to build projects for a **Jenkins Master**.  [2]

Jenkins runs a separate program called "**slave agent**" on slaves.
When slaves are registered to a master, the master starts distributing load to slaves by
scheduling jobs to run on slaves if the jobs are set to run on them.  [2]

Term **Node** is used to refer to all machines that are part of Jenkins grid, slaves and
master. [2]

Two types of slaves are currently connected to OPNFV Jenkins and handling
different tasks depending on the purpose of connecting the slave.

* Slaves hosted in `LF Lab <https://wiki.opnfv.org/get_started/lflab_hosting#hardware_setup>`_
* Slaves hosted in `Community Test Labs <https://wiki.opnfv.org/pharos#community_test_labs>`_

The slaves connected to OPNFV Jenkins can be seen using this link:
https://build.opnfv.org/ci/computer/

Slaves without red cross next to computer icon are fully functional.

Connecting Slaves to OPNFV Jenkins
==================================

The method that is normally used for connecting slaves to Jenkins requires direct SSH access to
servers.
[3] This is the method that is used for connecting slaves hosted in LF Lab.

Connecting slaves using direct SSH access can become a challenge given that OPNFV Project
has number of different labs provided by community as mentioned in previous section.
All these labs have different security requirements which can increase the effort
and the time needed for connecting slaves to Jenkins.
In order to reduce the effort and the time needed for connecting slaves and streamline the
process, it has been decided to connect slaves using
`Java Network Launch Protocol (JNLP) <https://docs.oracle.com/javase/tutorial/deployment/deploymentInDepth/jnlp.html>`_.

Connecting Slaves from LF Lab to OPNFV Jenkins
----------------------------------------------

Slaves hosted in LF Lab are handled by LF. All the requests and questions regarding
these slaves should be submitted to `OPNFV LF Helpdesk <opnfv-helpdesk@rt.linuxfoundation.org>`_.

Connecting Slaves from Community Labs to OPNFV Jenkins
------------------------------------------------------

As noted in corresponding section, slaves from Community Labs are connected using JNLP. Via JNLP,
slaves open connection towards Jenkins Master instead of Jenkins Master accessing to them directly.

Servers connecting to OPNFV Jenkins using this method must have access to internet.

Please follow below steps to connect a slave to OPNFV Jenkins.

  1. Create a user named **jenkins** on the machine you want to connect to OPNFV Jenkins and give the user sudo rights.
  2. Install needed software on the machine you want to connect to OPNFV Jenkins as slave.

    - openjdk 8
    - monit

  3. If the slave will be used for running virtual deployments, Functest, and Yardstick, install below software and make jenkins user the member of the groups.

    - docker
    - libvirt

  4. Create slave root in Jenkins user home directory.

    ``mkdir -p /home/jenkins/opnfv/slave_root``

  5. Clone OPNFV Releng Git repository.

    ``mkdir -p /home/jenkins/opnfv/repos``

    ``cd /home/jenkins/opnfv/repos``

    ``git clone https://gerrit.opnfv.org/gerrit/p/releng.git``

  6. Contact LF by sending mail to `OPNFV LF Helpdesk <opnfv-helpdesk@rt.linuxfoundation.org>`_ and request creation of a slave on OPNFV Jenkins. Include below information in your mail.

    - Slave root (/home/jenkins/opnfv/slave_root)
    - Public IP of the slave (You can get the IP by executing ``curl http://icanhazip.com/``)
    - PGP Key (attached to the mail or exported to a key server)

  7. Once you get confirmation from LF stating that your slave is created on OPNFV Jenkins, check if the firewall on LF is open for the server you are trying to connect to Jenkins.

    ``cp /home/jenkins/opnfv/repos/releng/utils/jenkins-jnlp-connect.sh /home/jenkins/``
    ``cd /home/jenkins/``
    ``sudo ./jenkins-jnlp-connect.sh -j /home/jenkins -u jenkins -n  <slave name on OPNFV Jenkins> -s <the token you received from LF> -f``

     - If you receive an error, follow the steps listed on the command output.

  8. Run the same script with test(-t) on foreground in order to make sure no problem on connection. You should see **INFO: Connected** in the console log.

    ``sudo ./jenkins-jnlp-connect.sh -j /home/jenkins -u jenkins -n <slave name on OPNFV Jenkins> -s <the token you received from LF> -t``

     - If you receive an error similar to the one shown `on this link <http://hastebin.com/ozadagirax.avrasm>`_, you need to check your firewall and allow outgoing connections for the port.

  9. Kill the Java slave.jar process.
  10. Run the same script normally without test(-t) in order to get monit script created.

    ``sudo ./jenkins-jnlp-connect.sh -j /home/jenkins -u jenkins -n <slave name on OPNFV Jenkins> -s <the token you received from LF>``

  11. Edit monit configuration and enable http interface. The file to edit is /etc/monit/monitrc on Ubuntu systems. Uncomment below lines.

    set httpd port 2812 and
        use address localhost  # only accept connection from localhost
        allow localhost        # allow localhost to connect to the server and

  12. Restart monit service.

    - Without systemd:

      ``sudo service monit restart``

    - With systemd: you have to enable monit service first and then restart it.

      ``sudo systemctl enable monit``

      ``sudo systemctl restart monit``

  13. Check to see if jenkins comes up as managed service in monit.

    ``sudo monit status``

  14. Connect slave to OPNFV Jenkins using monit.

    ``sudo monit start jenkins``

  15. Check slave on OPNFV Jenkins to verify the slave is reported as connected.

    - The slave on OPNFV Jenkins should have some executors in “Idle” state if the connection is successful.

Notes
==========

PGP Key Instructions
--------------------

Public PGP Key can be uploaded to public key server so it can be taken from
there using your mail address. Example command to upload the key to key server is

    ``gpg --keyserver hkp://keys.gnupg.net:80  --send-keys XXXXXXX``

The Public PGP Key can also be attached to the email by storing the key in a file and then
attaching it to the email.

    ``gpg --export -a '<your email address>' > pgp.pubkey``

References
==========

* `What is Jenkins <https://wiki.jenkins-ci.org/display/JENKINS/Meet+Jenkins>`_
* `Jenkins Terminology <https://wiki.jenkins-ci.org/display/JENKINS/Terminology>`_
* `Jenkins SSH Slaves Plugin <https://wiki.jenkins-ci.org/display/JENKINS/SSH+Slaves+plugin>`_
