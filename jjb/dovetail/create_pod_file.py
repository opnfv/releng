import sys
import os
import yaml
from opnfv.deployment import factory


def check_params(INSTALLER_TYPE, INSTALLER_IP, user, pkey, password):
    if not INSTALLER_TYPE or not INSTALLER_IP or not user:
        print("INSTALLER_TYPE, INSTALLER_IP and user are all needed.")
        return False
    if pkey == "nouse" and password == "nouse":
        print("pkey and password are all nouse. At least providing one")
        return False
    return True


def get_with_key(INSTALLER_TYPE, INSTALLER_IP, user, pkey):
    return factory.Factory.get_handler(INSTALLER_TYPE, INSTALLER_IP, user,
                                       pkey_file=pkey)


def get_with_passwd(INSTALLER_TYPE, INSTALLER_IP, user, password):
    return factory.Factory.get_handler(INSTALLER_TYPE, INSTALLER_IP, user,
                                       installer_pwd=password)


def create_file(INSTALLER_TYPE, handler, file_path):
    if not os.path.exists(os.path.dirname(file_path)):
        os.path.makedirs(os.path.dirname(file_path))
    nodes = handler.nodes
    node_list = []
    index = 1
    for node in nodes:
        node_info = {'name': 'node%s' % index, 'role': node.roles[0],
                     'ip': node.ip, 'user': 'root'}
        node_list.append(node_info)
        index += 1
    if INSTALLER_TYPE == 'compass':
        for item in node_list:
            item['password'] = 'root'
    else:
        for item in node_list:
            item['key_filename'] = '/root/.ssh/id_rsa'
    data = {'nodes': node_list}
    with open(file_path, "w") as fw:
        yaml.dump(data, fw)


def main():
    usage = "Usage: python create_pod_file.py INSTALLER_TYPE INSTALLER_IP \
             user pkey password"
    file_path = "/home/opnfv/dovetail/userconfig/pod.yaml"
    if len(sys.argv) != 6:
        print("Error: number of parameters is wrong")
        print(usage)
        return 1
    INSTALLER_TYPE = sys.argv[1]
    INSTALLER_IP = sys.argv[2]
    user = sys.argv[3]
    pkey = sys.argv[4]
    password = sys.argv[5]

    if not check_params(INSTALLER_TYPE, INSTALLER_IP, user, pkey, password):
        return 1
    if pkey != "nouse":
        handler = get_with_key(INSTALLER_TYPE, INSTALLER_IP, user, pkey)
    else:
        handler = get_with_passwd(INSTALLER_TYPE, INSTALLER_IP, user, password)
    if not handler:
        print("Error: failed to get the node's handler.")
        return 1
    create_file(INSTALLER_TYPE, handler, file_path)


if __name__ == '__main__':
    main()
