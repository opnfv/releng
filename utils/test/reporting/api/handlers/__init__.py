##############################################################################
# Copyright (c) 2017 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from tornado.web import RequestHandler


class BaseHandler(RequestHandler):
    def _set_header(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Content-Length, Authorization, \
                        Accept, X-Requested-With , PRIVATE-TOKEN')
        self.set_header('Access-Control-Allow-Methods',
                        'PUT, POST, GET, DELETE, OPTIONS')
