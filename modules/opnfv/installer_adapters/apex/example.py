# This is an example of usage of this Tool
# Author: Jose Lausuch (jose.lausuch@ericsson.com)

import opnfv.installer_adapters.InstallerHandler as ins_handler

apex_handler = InstallerHandler(installer='apex',
                                installer_user='stack')
apex_handler.get_file_from_installer(
    '/home/stack/undercloudrc', './undercloudrc')
