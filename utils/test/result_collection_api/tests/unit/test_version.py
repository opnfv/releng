import unittest

from test_base import TestBase

__author__ = 'serena'


class TestVersion(TestBase):
    def test_get_version(self):
        response = self.fetch('/version')
        self.assertEqual(response.code, 200)

if __name__ == '__main__':
    unittest.main()
