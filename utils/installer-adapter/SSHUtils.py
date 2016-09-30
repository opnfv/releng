##############################################################################
# Copyright (c) 2015 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


import paramiko
from scp import SCPClient
import time
import RelengLogger as rl


class SSH_Connection:

    def __init__(self,
                 host,
                 user,
                 password,
                 use_system_keys=True,
                 private_key=None,
                 use_proxy=False,
                 proxy_host=None,
                 proxy_user=None,
                 proxy_password=None,
                 timeout=10):
        self.host = host
        self.user = user
        self.password = password
        self.use_system_keys = use_system_keys
        self.private_key = private_key
        self.use_proxy = use_proxy
        self.proxy_host = proxy_host
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password
        self.timeout = timeout
        paramiko.util.log_to_file("paramiko.log")
        self.logger = rl.Logger("SSHUtils").getLogger()

    def connect(self):
        client = paramiko.SSHClient()
        if self.use_system_keys:
            client.load_system_host_keys()
        elif self.private_key:
            client.load_host_keys(self.private_key)
        else:
            client.load_host_keys('/dev/null')

        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        t = self.timeout
        proxy = None
        if self.use_proxy:
            proxy_command = 'ssh -o UserKnownHostsFile=/dev/null '
            '-o StrictHostKeyChecking=no %s@%s -W %s:%s' % (self.proxy_user,
                                                            self.proxy_host,
                                                            self.host, 22)
            proxy = paramiko.ProxyCommand(proxy_command)
            self.logger.debug("Proxy command: %s" % proxy_command)
        while t > 0:
            try:
                self.logger.debug(
                    "Trying to stablish ssh connection to %s..." % self.host)
                client.connect(self.host,
                               username=self.user,
                               password=self.password,
                               look_for_keys=True,
                               sock=proxy,
                               pkey=self.private_key,
                               timeout=self.timeout)
                self.logger.debug("Successfully connected to %s!" % self.host)
                return client
            except:
                time.sleep(1)
                t -= 1

        if t == 0:
            return None

    def scp_put(self, local_path, remote_path):
        client = self.connect()
        if client:
            scp = SCPClient(client.get_transport())
            try:
                scp.put(local_path, remote_path)
                client.close()
                return 0
            except Exception, e:
                self.logger.error(e)
                client.close()
                return 1
        else:
            self.logger.error("Cannot stablish ssh connection.")

    def scp_get(self, local_path, remote_path):
        client = self.connect()
        if client:
            scp = SCPClient(client.get_transport())
            try:
                scp.get(remote_path, local_path)
                client.close()
                return 0
            except Exception, e:
                self.logger.error(e)
                client.close()
                return 1
        else:
            self.logger.error("Cannot stablish ssh connection.")
            return 1

    def run_remote_cmd(self, command):
        client = self.connect()
        if client:
            try:
                stdin, stdout, stderr = client.exec_command(command)
                out = ''
                for line in stdout.readlines():
                    out += line
                err = stderr.readlines()
                client.close()
                return out, err
            except:
                client.close()
                return 1
        else:
            self.logger.error("Cannot stablish ssh connection.")
            return 1
