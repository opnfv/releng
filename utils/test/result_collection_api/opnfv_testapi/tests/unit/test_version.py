import unittest

from test_base import TestBase
from opnfv_testapi.resources.models import Versions

__author__ = 'serena'


class TestVersionBase(TestBase):
    def setUp(self):
        super(TestVersionBase, self).setUp()
        self.list_res = Versions
        self.basePath = '/versions'


class TestVersion(TestVersionBase):
    def test_success(self):
        code, body = self.get()
        self.assertEqual(200, code)
        self.assertEqual(len(body.versions), 1)
        self.assertEqual(body.versions[0].version, 'v1.0')
        self.assertEqual(body.versions[0].description, 'basics')

if __name__ == '__main__':
    unittest.main()
