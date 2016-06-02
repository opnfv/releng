##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import unittest

from test_base import TestBase
from opnfv_testapi.resources.models import Versions


class TestVersionbBase(TestBase):
    def setUp(self):
        super(TestVersionbBase, self).setUp()
        self.list_res = Versions
        self.basePath = '/versions'


class TestVersion(TestVersionbBase):
    def test_success(self):
        code, body = self.get()
        self.assertEqual(200, code)
        self.assertEqual(len(body.versions), 1)
        self.assertEqual(body.versions[0].version, 'v1.0')
        self.assertEqual(body.versions[0].description, 'basics')

if __name__ == '__main__':
    unittest.main()
