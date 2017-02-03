# This is an example of usage of this Tool
# Author: Jose Lausuch (jose.lausuch@ericsson.com)

from opnfv.utils import installer_handler as handler

apex_handler = handler.InstallerHandler(installer='apex',
                                        installer_ip='192.168.122.135',
                                        installer_user='stack',
                                        private_key_file='/root/.ssh/id_rsa')
apex_handler.get_file_from_installer(
    '/home/stack/overcloudrc', './overcloudrc')

print("\n%s\n" % apex_handler.get_deployment_info())

apex_handler.get_file_from_controller(
    '/etc/resolv.conf', './resolv.conf')
