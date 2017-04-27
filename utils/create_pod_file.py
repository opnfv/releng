import sys
import os
import yaml
from opnfv.deployment import factory
import argparse


parser = argparse.ArgumentParser(description='OPNFV POD Info Generator')

parser.add_argument("-t", "--INSTALLER_TYPE", help="Give INSTALLER_TYPE")
parser.add_argument("-i", "--INSTALLER_IP", help="Give INSTALLER_IP")
parser.add_argument("-u", "--user", help="Give username of this pod")
parser.add_argument("-k", "--key", help="Give key file of the user")
parser.add_argument("-p", "--password", help="Give password of the user")
parser.add_argument("-f", "--filepath", help="Give dest path of output file")
args = parser.parse_args()


def check_params():
    """
    Check all the CLI inputs. Must give INSTALLER_TYPE, INSTALLER_IP, user
    and filepath of the output file.
    Need to give key or password.
    """
    if not args.INSTALLER_TYPE or not args.INSTALLER_IP or not args.user:
        print("INSTALLER_TYPE, INSTALLER_IP and user are all needed.")
        return False
    if not args.key and not args.password:
        print("key and password are all None. At least providing one.")
        return False
    if not args.filepath:
        print("Must give the dest path of the output file.")
        return False
    return True


def get_with_key():
    """
    Get handler of the nodes info with key file.
    """
    return factory.Factory.get_handler(args.INSTALLER_TYPE, args.INSTALLER_IP,
                                       args.user, pkey_file=args.key)


def get_with_passwd():
    """
    Get handler of the nodes info with password.
    """
    return factory.Factory.get_handler(args.INSTALLER_TYPE, args.INSTALLER_IP,
                                       args.user, installer_pwd=args.password)


def create_file(handler):
    """
    Create the yaml file of nodes info.
    As Yardstick required, node name must be node1, node2, ... and node1 must
    be controller.
    Compass uses password of each node.
    Other installers use key file of each node.
    """
    if not os.path.exists(os.path.dirname(args.filepath)):
        os.path.makedirs(os.path.dirname(args.filepath))
    nodes = handler.nodes
    node_list = []
    index = 1
    for node in nodes:
        if node.roles[0].lower() == "controller":
            node_info = {'name': "node%s" % index, 'role': node.roles[0],
                         'ip': node.ip, 'user': 'root'}
            node_list.append(node_info)
            index += 1
    for node in nodes:
        if node.roles[0].lower() == "compute":
            node_info = {'name': "node%s" % index, 'role': node.roles[0],
                         'ip': node.ip, 'user': 'root'}
            node_list.append(node_info)
            index += 1
    if args.INSTALLER_TYPE == 'compass':
        for item in node_list:
            item['password'] = 'root'
    else:
        for item in node_list:
            item['key_filename'] = '/root/.ssh/id_rsa'
    data = {'nodes': node_list}
    with open(args.filepath, "w") as fw:
        yaml.dump(data, fw)


def main():
    if not check_params():
        return 1
    if args.key:
        handler = get_with_key()
    else:
        handler = get_with_passwd()
    if not handler:
        print("Error: failed to get the node's handler.")
        return 1
    create_file(handler)


if __name__ == '__main__':
    main()
