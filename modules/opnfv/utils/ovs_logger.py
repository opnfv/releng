##############################################################################
# Copyright (c) 2015 Ericsson AB and others.
# Author: George Paraskevopoulos (geopar@intracom-telecom.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

import opnfv.utils.opnfv_logger as OPNFVLogger
import os
import time
import shutil

logger = OPNFVLogger.Logger('ovs_logger').getLogger()


class OVSLogger(object):

    def __init__(self, basedir, ft_resdir):
        self.ovs_dir = basedir
        self.ft_resdir = ft_resdir
        self.__mkdir_p(self.ovs_dir)
        self.__mkdir_p(self.ft_resdir)

    def __mkdir_p(self, dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    def __ssh_host(self, ssh_conn, host_prefix=None):
        try:
            if host_prefix is None:
                raise Exception('The host prefix is not defined')
            else:
                _, stdout, _ = ssh_conn.exec_command('hostname -I')
                hosts = stdout.readline().strip().split(' ')
                found_host = [h for h in hosts if h.startswith(host_prefix)][0]
                return found_host
        except Exception as e:
            logger.error(e)

    def __dump_to_file(self, operation, host, text, timestamp=None):
        ts = (timestamp if timestamp is not None
              else time.strftime("%Y%m%d-%H%M%S"))
        dumpdir = os.path.join(self.ovs_dir, ts)
        self.__mkdir_p(dumpdir)
        fname = '{0}_{1}'.format(operation, host)
        with open(os.path.join(dumpdir, fname), 'w') as f:
            f.write(text)

    def __remote_cmd(self, ssh_conn, cmd, host_prefix=None):
        try:
            _, stdout, stderr = ssh_conn.exec_command(cmd)
            errors = stderr.readlines()
            if len(errors) > 0:
                host = self.__ssh_host(ssh_conn,
                                       host_prefix=host_prefix)
                logger.error(''.join(errors))
                raise Exception('Could not execute {0} in {1}'
                                .format(cmd, host))
            output = ''.join(stdout.readlines())
            return output
        except Exception as e:
            logger.error('[__remote_command(ssh_client, {0})]: {1}'
                         .format(cmd, e))
            return None

    def create_artifact_archive(self):
        shutil.make_archive(self.ovs_dir,
                            'zip',
                            root_dir=os.path.dirname(self.ovs_dir),
                            base_dir=self.ovs_dir)
        shutil.copy2('{0}.zip'.format(self.ovs_dir), self.ft_resdir)

    def ofctl_dump_flows(self, ssh_conn, br='br-int',
                         choose_table=None, timestamp=None,
                         host_prefix=None):
        try:
            cmd = 'ovs-ofctl -OOpenFlow13 dump-flows {0}'.format(br)
            if choose_table is not None:
                cmd = '{0} table={1}'.format(cmd, choose_table)
            output = self.__remote_cmd(ssh_conn, cmd,
                                       host_prefix=host_prefix)
            operation = 'ofctl_dump_flows'
            host = self.__ssh_host(ssh_conn,
                                   host_prefix=host_prefix)
            self.__dump_to_file(operation, host, output, timestamp=timestamp)
            return output
        except Exception as e:
            logger.error('[ofctl_dump_flows(ssh_client, {0}, {1})]: {2}'
                         .format(br, choose_table, e))
            return None

    def vsctl_show(self, ssh_conn, timestamp=None,
                   host_prefix=None):
        try:
            cmd = 'ovs-vsctl show'
            output = self.__remote_cmd(ssh_conn, cmd,
                                       host_prefix=host_prefix)
            operation = 'vsctl_show'
            host = self.__ssh_host(ssh_conn,
                                   host_prefix=host_prefix)
            self.__dump_to_file(operation, host, output, timestamp=timestamp)
            return output
        except Exception as e:
            logger.error('[vsctl_show(ssh_client)]: {0}'.format(e))
            return None

    def dump_ovs_logs(self, controller_clients, compute_clients,
                      host_prefix=None, related_error=None,
                      timestamp=None):
        if timestamp is None:
            timestamp = time.strftime("%Y%m%d-%H%M%S")

        clients = controller_clients + compute_clients
        for client in clients:
            self.ofctl_dump_flows(client, timestamp=timestamp,
                                  host_prefix=None)
            self.vsctl_show(client, timestamp=timestamp,
                            host_prefix=None)

        if related_error is not None:
            dumpdir = os.path.join(self.ovs_dir, timestamp)
            self.__mkdir_p(dumpdir)
            with open(os.path.join(dumpdir, 'error'), 'w') as f:
                f.write(related_error)
