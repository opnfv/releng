##############################################################################
# Copyright (c) 2017 Ericsson AB and others.
# Author: Jose Lausuch (jose.lausuch@ericsson.com)
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


from opnfv.deployment.apex import adapter as apex_adapter
from opnfv.deployment.fuel import adapter as fuel_adapter
from opnfv.utils import opnfv_logger as logger

logger = logger.Logger(__name__).getLogger()


class Factory(object):

    INSTALLERS = ["fuel", "apex", "compass", "joid", "daisy"]

    def __init__(self):
        pass

    @staticmethod
    def get_handler(installer,
                    installer_ip,
                    installer_user,
                    installer_pwd=None,
                    pkey_file=None):

        if installer not in Factory.INSTALLERS:
            raise Exception("This is not an OPNFV installer.")

        if installer.lower() == "apex":
            return apex_adapter.ApexAdapter(installer_ip=installer_ip,
                                            installer_user=installer_user,
                                            pkey_file=pkey_file)
        elif installer.lower() == "fuel":
            return fuel_adapter.FuelAdapter(installer_ip=installer_ip,
                                            installer_user=installer_user,
                                            installer_pwd=installer_pwd)
        else:
            raise Exception("Installer adapter is not implemented.")
