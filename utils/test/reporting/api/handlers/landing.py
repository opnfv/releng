##############################################################################
# Copyright (c) 2016 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from tornado.web import RequestHandler
from tornado.escape import json_encode


class FiltersHandler(RequestHandler):
    def get(self):
        return self.write(json_encode({'status': 'SUCCESS'}))


class ScenariosHandler(RequestHandler):
    def get(self):
        return self.write(json_encode({'status': 'SUCCESS'}))
