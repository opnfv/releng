##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

"""
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('config.ini')


mongo_url = parser.get('default', 'mongo_url')
"""


def prepare_put_request(edit_request, key, new_value, old_value):
    """
    This function serves to prepare the elements in the update request.
    We try to avoid replace the exact values in the db
    edit_request should be a dict in which we add an entry (key) after comparing values
    """
    if not (new_value is None):
        if len(new_value) > 0:
            if new_value != old_value:
                edit_request[key] = new_value

    return edit_request
