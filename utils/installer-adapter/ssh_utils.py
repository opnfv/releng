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


class SSH_Connection:

    def __init__(self,
                 host,
                 user,
                 password,
                 use_proxy=False,
                 proxy_host=None,
                 proxy_user=None,
                 proxy_password=None,
                 timeout=60):
        self.host = host
        self.user = user
        self.password = password
        self.use_proxy = use_proxy
        self.proxy_host = proxy_host
        self.proxy_user = proxy_user
        self.proxy_password = proxy_password
        self.timeout = timeout

    def connect(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        t = self.timeout
        while t > 0:
            try:
                proxy = None
                if self.use_proxy:
                    proxy_command = 'ssh %s@%s -W %s:%s' % (self.proxy_user,
                                                            self.proxy_host,
                                                            self.host, 22)
                    proxy = paramiko.ProxyCommand(proxy_command)

                client.connect(self.host,
                               username=self.user,
                               password=self.password,
                               look_for_keys=True,
                               sock=proxy,
                               timeout=10)
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
                ret_val = scp.put(local_path, remote_path)
                client.close()
                return ret_val
            except Exception, e:
                print(e)
                client.close()
                return 1
        else:
            print("Cannot stablish ssh connection.")

    def scp_get(self, local_path, remote_path):
        client = self.connect()
        if client:
            scp = SCPClient(client.get_transport())
            try:
                ret_val = scp.get(remote_path, local_path)
                client.close()
                return ret_val
            except Exception, e:
                print(e)
                client.close()
                return 1
        else:
            print("Cannot stablish ssh connection.")
            return 1

    def run_remote_cmd(self, command):
        client = self.connect()
        if client:
            try:
                stdin, stdout, stderr = client.exec_command(command)
                out = stdout.readlines()
                err = stderr.readlines()
                client.close()
                return out, err
            except:
                client.close()
                return 1
        else:
            print("Cannot stablish ssh connection.")
            return 1
