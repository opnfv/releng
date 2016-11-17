#!/usr/bin/env python

# Copyright (c) 2016 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0


import os
import time


class Connection(object):

    def __init__(self):
        pass

    def verify_connectivity(self, target):
        for x in range(0, 10):
            ping_cmd = ("ping -c 1 -W 1 %s >/dev/null" % target)
            response = os.system(ping_cmd)
            if response == 0:
                return os.EX_OK
            time.sleep(1)
        return os.EX_UNAVAILABLE

    def check_internet_access(self, url="www.google.com"):
        return self.verify_connectivity(url)
