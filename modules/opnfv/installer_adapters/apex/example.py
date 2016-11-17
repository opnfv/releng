# This is an example of usage of this Tool
# Author: Jose Lausuch (jose.lausuch@ericsson.com)

import opnfv.installer_adapters.InstallerHandler as ins_handler

apex_handler = ins_handler.InstallerHandler(installer='apex',
                                            installer_ip='192.168.122.135',
                                            installer_user='stack')
apex_handler.get_file_from_installer(
    '/home/stack/overcloudrc', './overcloudrc')
