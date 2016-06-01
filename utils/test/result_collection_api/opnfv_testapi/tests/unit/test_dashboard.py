import unittest

from test_result import TestResultBase
from opnfv_testapi.common.constants import HTTP_NOT_FOUND, HTTP_OK

__author__ = '__serena__'


class TestDashboardBase(TestResultBase):
    def setUp(self):
        super(TestDashboardBase, self).setUp()
        self.basePath = '/dashboard/v1/results'
        self.create_help('/api/v1/results', self.req_d)
        self.create_help('/api/v1/results', self.req_d)
        self.list_res = None


class TestDashboardQuery(TestDashboardBase):
    def test_projectMissing(self):
        code, body = self.query(self._set_query(project='missing'))
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn('Project name missing', body)

    def test_projectNotReady(self):
        code, body = self.query(self._set_query(project='notReadyProject'))
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn('Project [notReadyProject] not dashboard ready', body)

    def test_testcaseMissing(self):
        code, body = self.query(self._set_query(case='missing'))
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn('Test case missing for project [{}]'
                      .format(self.project),
                      body)

    def test_testcaseNotReady(self):
        code, body = self.query(self._set_query(case='notReadyCase'))
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn(
            'Test case [notReadyCase] not dashboard ready for project [%s]'
            % self.project,
            body)

    def test_success(self):
        code, body = self.query(self._set_query())
        self.assertEqual(code, HTTP_OK)
        self.assertIn('{"description": "vPing results for Dashboard"}', body)

    def test_caseIsStatus(self):
        code, body = self.query(self._set_query(case='status'))
        self.assertEqual(code, HTTP_OK)
        self.assertIn('{"description": "Functest status"}', body)

    def _set_query(self, project=None, case=None):
        uri = ''
        for k, v in list(locals().iteritems()):
            if k == 'self' or k == 'uri':
                continue
            if v is None:
                v = eval('self.' + k)
            if v != 'missing':
                uri += '{}={}&'.format(k, v)
        uri += 'pod={}&'.format(self.pod)
        uri += 'version={}&'.format(self.version)
        uri += 'installer={}&'.format(self.installer)
        uri += 'period={}&'.format(5)
        return uri[0:-1]


if __name__ == '__main__':
    unittest.main()
