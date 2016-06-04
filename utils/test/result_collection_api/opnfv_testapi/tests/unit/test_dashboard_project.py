import json

from opnfv_testapi.common.constants import HTTP_OK
from test_base import TestBase


class TestDashboardProjectBase(TestBase):
    def setUp(self):
        super(TestDashboardProjectBase, self).setUp()
        self.basePath = '/dashboard/v1/projects'
        self.list_res = None
        self.projects = ['bottlenecks', 'doctor', 'functest',
                         'promise', 'qtip', 'vsperf', 'yardstick']


class TestDashboardProjectGet(TestDashboardProjectBase):
    def test_list(self):
        code, body = self.get()
        self.assertEqual(code, HTTP_OK)
        self.assertItemsEqual(self.projects, json.loads(body))
