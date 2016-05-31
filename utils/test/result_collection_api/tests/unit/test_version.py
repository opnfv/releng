import json
import unittest

from test_base import TestBase

__author__ = 'serena'


class TestVersionbBase(TestBase):
    def setUp(self):
        super(TestVersionbBase, self).setUp()
        self.list_res = None
        self.basePath = '/versions'


class TestVersion(TestVersionbBase):
    def test_success(self):
        code, body = self.get()
        self.assertEqual(200, code)
        json_body = json.loads(body)
        self.assertEqual(len(json_body), 1)
        self.assertEqual('v1.0', json_body[0].get('version'))
        self.assertEqual('basics', json_body[0].get('description'))


if __name__ == '__main__':
    unittest.main()
