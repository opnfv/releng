##############################################################################
# Copyright (c) 2017 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import requests

from tornado.escape import json_encode

from api.handlers import BaseHandler
from api import conf


class TestCases(BaseHandler):
    def get(self, project):
        self._set_header()

        url = '{}/projects/{}/cases'.format(conf.base_url, project)
        cases = requests.get(url).json().get('testcases', [])
        data = [{t['name']: t['catalog_description']} for t in cases]
        self.write(json_encode(data))


class TestCase(BaseHandler):
    def get(self, project, name):
        self._set_header()

        url = '{}/projects/{}/cases/{}'.format(conf.base_url, project, name)
        data = requests.get(url).json()
        self.write(json_encode(data))
