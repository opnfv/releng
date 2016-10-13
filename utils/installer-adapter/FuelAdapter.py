##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


from SSHUtils import SSH_Connection
import RelengLogger as rl


class FuelAdapter:

    def __init__(self, installer_ip, user="root", password="r00tme"):
        self.installer_ip = installer_ip
        self.user = user
        self.password = password
        self.connection = SSH_Connection(
            installer_ip, self.user, self.password, use_system_keys=False)
        self.logger = rl.Logger("Handler").getLogger()

    def runcmd_fuel_nodes(self):
        output, error = self.connection.run_remote_cmd('fuel nodes')
        if len(error) > 0:
            self.logger.error("error %s" % error)
            return error
        return output

    def runcmd_fuel_env(self):
        output, error = self.connection.run_remote_cmd('fuel env')
        if len(error) > 0:
            self.logger.error("error %s" % error)
            return error
        return output

    def get_clusters(self):
        environments = []
        output = self.runcmd_fuel_env()
        lines = output.rsplit('\n')
        if len(lines) < 2:
            self.logger.infp("No environments found in the deployment.")
            return None
        else:
            fields = lines[0].rsplit(' | ')

            index_id = -1
            index_status = -1
            index_name = -1
            index_release_id = -1

            for i in range(0, len(fields) - 1):
                if "id" in fields[i]:
                    index_id = i
                elif "status" in fields[i]:
                    index_status = i
                elif "name" in fields[i]:
                    index_name = i
                elif "release_id" in fields[i]:
                    index_release_id = i

            # order env info
            for i in range(2, len(lines) - 1):
                fields = lines[i].rsplit(' | ')
                dict = {"id": fields[index_id].strip(),
                        "status": fields[index_status].strip(),
                        "name": fields[index_name].strip(),
                        "release_id": fields[index_release_id].strip()}
                environments.append(dict)

        return environments

    def get_nodes(self, options=None):
        nodes = []
        output = self.runcmd_fuel_nodes()
        lines = output.rsplit('\n')
        if len(lines) < 2:
            self.logger.info("No nodes found in the deployment.")
            return None
        else:
            # get fields indexes
            fields = lines[0].rsplit(' | ')

            index_id = -1
            index_status = -1
            index_name = -1
            index_cluster = -1
            index_ip = -1
            index_mac = -1
            index_roles = -1
            index_online = -1

            for i in range(0, len(fields) - 1):
                if "id" in fields[i]:
                    index_id = i
                elif "status" in fields[i]:
                    index_status = i
                elif "name" in fields[i]:
                    index_name = i
                elif "cluster" in fields[i]:
                    index_cluster = i
                elif "ip" in fields[i]:
                    index_ip = i
                elif "mac" in fields[i]:
                    index_mac = i
                elif "roles " in fields[i]:
                    index_roles = i
                elif "online" in fields[i]:
                    index_online = i

            # order nodes info
            for i in range(2, len(lines) - 1):
                fields = lines[i].rsplit(' | ')
                dict = {"id": fields[index_id].strip(),
                        "status": fields[index_status].strip(),
                        "name": fields[index_name].strip(),
                        "cluster": fields[index_cluster].strip(),
                        "ip": fields[index_ip].strip(),
                        "mac": fields[index_mac].strip(),
                        "roles": fields[index_roles].strip(),
                        "online": fields[index_online].strip()}
                if options and options['cluster']:
                    if fields[index_cluster].strip() == options['cluster']:
                        nodes.append(dict)
                else:
                    nodes.append(dict)

        return nodes

    def get_controller_ips(self, options):
        nodes = self.get_nodes(options=options)
        controllers = []
        for node in nodes:
            if "controller" in node["roles"]:
                controllers.append(node['ip'])
        return controllers

    def get_compute_ips(self, options=None):
        nodes = self.get_nodes(options=options)
        computes = []
        for node in nodes:
            if "compute" in node["roles"]:
                computes.append(node['ip'])
        return computes

    def get_deployment_info(self):
        str = "Deployment details:\n"
        str += "\tInstaller:  Fuel\n"
        str += "\tScenario:   Unknown\n"
        sdn = "None"
        clusters = self.get_clusters()
        str += "\tN.Clusters: %s\n" % len(clusters)
        for cluster in clusters:
            cluster_dic = {'cluster': cluster['id']}
            str += "\tCluster info:\n"
            str += "\t   ID:          %s\n" % cluster['id']
            str += "\t   NAME:        %s\n" % cluster['name']
            str += "\t   STATUS:      %s\n" % cluster['status']
            nodes = self.get_nodes(options=cluster_dic)
            num_nodes = len(nodes)
            for node in nodes:
                if "opendaylight" in node['roles']:
                    sdn = "OpenDaylight"
                elif "onos" in node['roles']:
                    sdn = "ONOS"
            num_controllers = len(
                self.get_controller_ips(options=cluster_dic))
            num_computes = len(self.get_compute_ips(options=cluster_dic))
            ha = False
            if num_controllers > 1:
                ha = True

            str += "\t   HA:          %s\n" % ha
            str += "\t   NUM.NODES:   %s\n" % num_nodes
            str += "\t   CONTROLLERS: %s\n" % num_controllers
            str += "\t   COMPUTES:    %s\n" % num_computes
            str += "\t   SDN CONTR.:  %s\n\n" % sdn
        str += self.runcmd_fuel_nodes()
        return str

    def get_file_from_installer(self, remote_path, local_path, options=None):
        self.logger.debug("Fetching %s from %s" %
                          (remote_path, self.installer_ip))
        if self.connection.scp_get(local_path, remote_path) != 0:
            self.logger.error("SCP failed to retrieve the file.")
            return 1
        self.logger.info("%s successfully copied from Fuel to %s" %
                         (remote_path, local_path))

    def get_file_from_controller(self,
                                 remote_path,
                                 local_path,
                                 ip=None,
                                 options=None):
        if ip is None:
            controllers = self.get_controller_ips(options=options)
            if len(controllers) == 0:
                self.logger.info("No controllers found in the deployment.")
                return 1
            else:
                target_ip = controllers[0]
        else:
            target_ip = ip

        fuel_dir = '/root/scp/'
        cmd = 'mkdir -p %s;rsync -Rav %s:%s %s' % (
            fuel_dir, target_ip, remote_path, fuel_dir)
        self.logger.info("Copying %s from %s to Fuel..." %
                         (remote_path, target_ip))
        output, error = self.connection.run_remote_cmd(cmd)
        self.logger.debug("Copying files from Fuel to %s..." % local_path)
        self.get_file_from_installer(
            fuel_dir + remote_path, local_path, options)
        cmd = 'rm -r %s' % fuel_dir
        output, error = self.connection.run_remote_cmd(cmd)
        self.logger.info("%s successfully copied from %s to %s" %
                         (remote_path, target_ip, local_path))
