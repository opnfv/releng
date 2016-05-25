import unittest

from test_base import TestBase
from resources.pod_models import PodCreateRequest
from resources.project_models import ProjectCreateRequest
from resources.testcase_models import TestcaseCreateRequest
from resources.result_models import ResultCreateRequest, \
    TestResult, TestResults
from common.constants import HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND


__author__ = '__serena__'


class Details(object):
    def __init__(self, timestart=None, duration=None, status=None):
        self.timestart = timestart
        self.duration = duration
        self.status = status

    def format(self):
        return {
            "timestart": self.timestart,
            "duration": self.duration,
            "status": self.status
        }

    @staticmethod
    def from_dict(a_dict):

        if a_dict is None:
            return None

        t = Details()
        t.timestart = a_dict.get('timestart')
        t.duration = a_dict.get('duration')
        t.status = a_dict.get('status')
        return t


class TestResultBase(TestBase):
    def setUp(self):
        self.pod = 'zte-pod1'
        self.project = 'functest'
        self.case = 'vPing'
        self.installer = 'fuel'
        self.version = 'C'
        self.build_tag = 'v3.0'
        self.scenario = 'odl-l2'
        self.criteria = '10s'
        self.trust_indicator = 0.7
        super(TestResultBase, self).setUp()
        self.details = Details(timestart='0', duration='9s', status='OK')
        self.req_d = ResultCreateRequest(pod_name=self.pod,
                                         project_name=self.project,
                                         case_name=self.case,
                                         installer=self.installer,
                                         version=self.version,
                                         description='vping use ssh',
                                         details=self.details.format(),
                                         build_tag=self.build_tag,
                                         scenario=self.scenario,
                                         criteria=self.criteria,
                                         trust_indicator=self.trust_indicator)
        self.get_res = TestResult
        self.list_res = TestResults
        self.basePath = '/v1/results'
        self.req_pod = PodCreateRequest(self.pod, 'metal', 'zte pod 1')
        self.req_project = ProjectCreateRequest(self.project, 'vping test')
        self.req_testcase = TestcaseCreateRequest('/cases/vping',
                                                  self.case,
                                                  'vping-ssh test')
        self.create_help('/v1/pods', self.req_pod)
        self.create_help('/v1/projects', self.req_project)
        self.create_help('/v1/projects/%s/cases', self.req_testcase, self.project)

    def assert_res(self, code, result):
        self.assertEqual(code, HTTP_OK)
        req = self.req_d
        self.assertEqual(result.pod_name, req.pod_name)
        self.assertEqual(result.project_name, req.project_name)
        self.assertEqual(result.case_name, req.case_name)
        self.assertEqual(result.installer, req.installer)
        self.assertEqual(result.version, req.version)
        self.assertEqual(result.description, req.description)
        details_req = Details.from_dict(req.details)
        details_res = Details.from_dict(result.details)
        self.assertEqual(details_res.duration, details_req.duration)
        self.assertEqual(details_res.timestart, details_req.timestart)
        self.assertEqual(details_res.status, details_req.status)
        self.assertEqual(result.build_tag, req.build_tag)
        self.assertEqual(result.scenario, req.scenario)
        self.assertEqual(result.criteria, req.criteria)
        self.assertEqual(result.trust_indicator, req.trust_indicator)
        self.assertIsNotNone(result.creation_date)
        self.assertIsNotNone(result._id)


class TestResultCreate(TestResultBase):
    def test_nobody(self):
        (code, body) = self.create(None)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('no payload', body)

    def test_podNotProvided(self):
        req = self.req_d
        req.pod_name = None
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('pod is not provided', body)

    def test_projectNotProvided(self):
        req = self.req_d
        req.project_name = None
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('project is not provided', body)

    def test_testcaseNotProvided(self):
        req = self.req_d
        req.case_name = None
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('testcase is not provided', body)

    def test_noPod(self):
        req = self.req_d
        req.pod_name = 'notExistPod'
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn('Could not find POD', body)

    def test_noProject(self):
        req = self.req_d
        req.project_name = 'notExistProject'
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn('Could not find project', body)

    def test_noTestcase(self):
        req = self.req_d
        req.case_name = 'notExistTestcase'
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn('Could not find testcase', body)

    def test_success(self):
        (code, body) = self.create_d()
        self.assertEqual(code, HTTP_OK)
        self.assert_href(body)


class TestResultGet(TestResultBase):
    def test_getOne(self):
        _, res = self.create_d()
        _id = res.href.split('/')[-1]
        code, body = self.get(_id)
        self.assert_res(code, body)

    def test_queryPod(self):
        self._query_and_assert(self._set_query('pod'))

    def test_queryProject(self):
        self._query_and_assert(self._set_query('project'))

    def test_queryTestcase(self):
        self._query_and_assert(self._set_query('case'))

    def test_queryVersion(self):
        self._query_and_assert(self._set_query('version'))

    def test_queryInstaller(self):
        self._query_and_assert(self._set_query('installer'))

    def test_queryBuildTag(self):
        self._query_and_assert(self._set_query('build_tag'))

    def test_queryScenario(self):
        self._query_and_assert(self._set_query('scenario'))

    def test_queryTrustIndicator(self):
        self._query_and_assert(self._set_query('trust_indicator'))

    def test_queryCriteria(self):
        self._query_and_assert(self._set_query('criteria'))

    def test_queryPeriod(self):
        self._query_and_assert(self._set_query('period=1'))

    def test_combination(self):
        self._query_and_assert(self._set_query('pod',
                                               'project',
                                               'case',
                                               'version',
                                               'installer',
                                               'build_tag',
                                               'scenario',
                                               'trust_indicator',
                                               'criteria',
                                               'period=1'))

    def test_notFound(self):
        self._query_and_assert(self._set_query('pod=notExistPod',
                                               'project',
                                               'case',
                                               'version',
                                               'installer',
                                               'build_tag',
                                               'scenario',
                                               'trust_indicator',
                                               'criteria',
                                               'period=1'),
                               found=False)

    def _query_and_assert(self, query, found=True):
        _, res = self.create_d()
        code, body = self.query(query)
        if not found:
            self.assertEqual(code, HTTP_OK)
            self.assertEqual(0, len(body.results))
        else:
            for result in body.results:
                self.assert_res(code, result)

    def _set_query(self, *args):
        uri = ''
        for arg in args:
            if '=' in arg:
                uri += arg + '&'
            else:
                uri += '{}={}&'.format(arg, eval('self.' + arg))
        return uri[0: -1]

if __name__ == '__main__':
    unittest.main()
