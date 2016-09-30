##############################################################################
# Copyright (c) 2016 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


from SSHUtils import SSH_Connection


class FuelAdapter:

    def __init__(self, installer_ip, user="root", password="r00tme"):
        self.installer_ip = installer_ip
        self.user = user
        self.password = password
        self.connection = SSH_Connection(
            installer_ip, self.user, self.password, use_system_keys=False)

    def get_deployment_info(self):
        return self.get_controller_ips()

    def get_nodes(self):
        nodes = []
        output, error = self.connection.run_remote_cmd('fuel nodes')
        lines = output.rsplit('\n')
        if len(lines) < 2:
            print("No nodes found in the deployment.")
            return None
        else:
            # get fields indexes
            fields = lines[0].rsplit(' | ')

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
                nodes.append(dict)

        return nodes

    def get_controller_ips(self):
        nodes = self.get_nodes()
        controllers = []
        for node in nodes:
            if "controller" in node["roles"]:
                controllers.append(node['ip'])
        return controllers

    def get_compute_ips(self):
        nodes = self.get_nodes()
        computes = []
        for node in nodes:
            if "compute" in node["roles"]:
                computes.append(node['ip'])
        return computes
