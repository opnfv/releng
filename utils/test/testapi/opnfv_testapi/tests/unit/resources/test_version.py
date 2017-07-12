##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import httplib
import unittest

from opnfv_testapi.resources import models
from opnfv_testapi.tests.unit import executor
from opnfv_testapi.tests.unit.resources import test_base as base


class TestVersionBase(base.TestBase):
    def setUp(self):
        super(TestVersionBase, self).setUp()
        self.list_res = models.Versions
        self.basePath = '/versions'


class TestVersion(TestVersionBase):
    @executor.get(httplib.OK, '_get_success')
    def test_success(self):
        return None

    def _get_success(self, body):
        self.assertEqual(len(body.versions), 1)
        self.assertEqual(body.versions[0].version, 'v1.0')
        self.assertEqual(body.versions[0].description, 'basics')


if __name__ == '__main__':
    unittest.main()
