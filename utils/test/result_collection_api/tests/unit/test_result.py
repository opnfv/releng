import unittest

from test_base import TestBase
from resources.pod_models import PodCreateRequest
from resources.project_models import ProjectCreateRequest
from resources.testcase_models import TestcaseCreateRequest
from resources.result_models import ResultCreateRequest, \
    TestResult, TestResults, Details
from common.constants import HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND


__author__ = '__serena__'


class TestResultBase(TestBase):
    def setUp(self):
        self.pod = 'zte-pod1'
        self.project = 'vping'
        self.testcase = 'vping-ssh'
        self.installer = 'fuel'
        self.version = 'C'
        self.build_tag = 'v3.0'
        self.scenario = 'odl-l2'
        self.criteria = '10s'
        self.trust_indicator = 0.7
        super(TestResultBase, self).setUp()
        self.details = Details(timestart='0', duration='9s', status='ok')
        self.req_d = ResultCreateRequest(pod_name=self.pod,
                                         project_name=self.project,
                                         case_name=self.testcase,
                                         installer=self.installer,
                                         version=self.version,
                                         description='vping use ssh',
                                         details=self.details,
                                         build_tag=self.build_tag,
                                         scenario=self.scenario,
                                         criteria=self.criteria,
                                         trust_indicator=self.trust_indicator)
        self.get_res = TestResult
        self.list_res = TestResults
        self.basePath = '/results'
        self.req_pod = PodCreateRequest(self.pod, 'fuel', 'zte pod 1')
        self.req_project = ProjectCreateRequest(self.project, 'vping test')
        self.req_testcase = TestcaseCreateRequest('/cases/vping',
                                                  'vping-ssh',
                                                  'vping-ssh test')
        self.create_help('/pods', self.req_pod)
        self.create_help('/projects', self.req_project)
        self.create_help('/projects/%s/cases', self.req_testcase, self.project)

    def assert_res(self, code, result):
        self.assertEqual(code, HTTP_OK)
        req = self.req_d
        self.assertEqual(result.pod_name, req.pod_name)
        self.assertEqual(result.project_name, req.project_name)
        self.assertEqual(result.case_name, req.case_name)
        self.assertEqual(result.installer, req.installer)
        self.assertEqual(result.version, req.version)
        self.assertEqual(result.description, req.description)
        self.assertEqual(result.details.duration, req.details.duration)
        self.assertEqual(result.details.timestart, req.details.timestart)
        self.assertEqual(result.details.status, req.details.status)
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
        req = ResultCreateRequest(project_name=self.project,
                                  case_name=self.testcase,
                                  installer=self.installer,
                                  version='C',
                                  description='vping use ssh',
                                  details=self.details,
                                  build_tag='v3.0',
                                  scenario='odl-l2',
                                  criteria='10s',
                                  trust_indicator=0.7)
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('pod is not provided', body)

    def test_projectNotProvided(self):
        req = ResultCreateRequest(pod_name=self.pod,
                                  case_name=self.testcase,
                                  installer=self.installer,
                                  version='C',
                                  description='vping use ssh',
                                  details=self.details,
                                  build_tag='v3.0',
                                  scenario='odl-l2',
                                  criteria='10s',
                                  trust_indicator=0.7)
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('project is not provided', body)

    def test_testcaseNotProvided(self):
        req = ResultCreateRequest(pod_name=self.pod,
                                  project_name=self.project,
                                  installer=self.installer,
                                  version='C',
                                  description='vping use ssh',
                                  details=self.details,
                                  build_tag='v3.0',
                                  scenario='odl-l2',
                                  criteria='10s',
                                  trust_indicator=0.7)
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('testcase is not provided', body)

    def test_noPod(self):
        req = ResultCreateRequest(pod_name='notExistPod',
                                  project_name=self.project,
                                  case_name=self.testcase,
                                  installer=self.installer,
                                  version='C',
                                  description='vping use ssh',
                                  details=self.details,
                                  build_tag='v3.0',
                                  scenario='odl-l2',
                                  criteria='10s',
                                  trust_indicator=0.7)
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn('Could not find POD', body)

    def test_noProject(self):
        req = ResultCreateRequest(pod_name=self.pod,
                                  project_name='notExistProject',
                                  case_name=self.testcase,
                                  installer=self.installer,
                                  version='C',
                                  description='vping use ssh',
                                  details=self.details,
                                  build_tag='v3.0',
                                  scenario='odl-l2',
                                  criteria='10s',
                                  trust_indicator=0.7)
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn('Could not find project', body)

    def test_noTestcase(self):
        req = ResultCreateRequest(pod_name=self.pod,
                                  project_name=self.project,
                                  case_name='notExistTestcase',
                                  installer=self.installer,
                                  version='C',
                                  description='vping use ssh',
                                  details=self.details,
                                  build_tag='v3.0',
                                  scenario='odl-l2',
                                  criteria='10s',
                                  trust_indicator=0.7)
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
        self._query_and_assert('pod={}'.format(self.pod))

    def test_queryProject(self):
        self._query_and_assert('project={}'.format(self.project))

    def test_queryTestcase(self):
        self._query_and_assert('case={}'.format(self.testcase))

    def test_queryVersion(self):
        self._query_and_assert('version={}'.format(self.version))

    def test_queryInstaller(self):
        self._query_and_assert('installer={}'.format(self.installer))

    def test_queryBuildTag(self):
        self._query_and_assert('build_tag={}'.format(self.build_tag))

    def test_queryScenario(self):
        self._query_and_assert('scenario={}'.format(self.scenario))

    def test_queryTrustIndicator(self):
        self._query_and_assert('trust_indicator={}'
                               .format(self.trust_indicator))

    def test_queryCriteria(self):
        self._query_and_assert('criteria={}'.format(self.criteria))

    def test_queryPeriod(self):
        self._query_and_assert('period={}'.format(1))

    def test_combination(self):
        self._query_and_assert('pod={}&'
                               'project={}&'
                               'case={}&'
                               'version={}&'
                               'installer={}&'
                               'build_tag={}&'
                               'scenario={}&'
                               'trust_indicator={}&'
                               'criteria={}&'
                               'period={}'
                               .format(self.pod, self.project,
                                       self.testcase, self.version,
                                       self.installer, self.build_tag,
                                       self.scenario, self.trust_indicator,
                                       self.criteria, 1))

    def test_notFound(self):
        self._query_and_assert('pod={}&'
                               'project={}&'
                               'case={}&'
                               'version={}&'
                               'installer={}&'
                               'build_tag={}&'
                               'scenario={}&'
                               'trust_indicator={}&'
                               'criteria={}&'
                               'period={}'
                               .format('notExistPod', self.project,
                                       self.testcase, self.version,
                                       self.installer, self.build_tag,
                                       self.scenario, self.trust_indicator,
                                       self.criteria, 1),
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


if __name__ == '__main__':
    unittest.main()
