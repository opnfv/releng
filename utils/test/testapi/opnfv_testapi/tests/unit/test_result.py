##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import copy
import unittest
from datetime import datetime, timedelta

from opnfv_testapi.common.constants import HTTP_OK, HTTP_BAD_REQUEST, \
    HTTP_NOT_FOUND
from opnfv_testapi.resources.pod_models import PodCreateRequest
from opnfv_testapi.resources.project_models import ProjectCreateRequest
from opnfv_testapi.resources.result_models import ResultCreateRequest, \
    TestResult, TestResults, ResultUpdateRequest, TI, TIHistory
from opnfv_testapi.resources.testcase_models import TestcaseCreateRequest
from test_base import TestBase


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
        self.criteria = 'passed'
        self.trust_indicator = TI(0.7)
        self.start_date = "2016-05-23 07:16:09.477097"
        self.stop_date = "2016-05-23 07:16:19.477097"
        self.update_date = "2016-05-24 07:16:19.477097"
        self.update_step = -0.05
        super(TestResultBase, self).setUp()
        self.details = Details(timestart='0', duration='9s', status='OK')
        self.req_d = ResultCreateRequest(pod_name=self.pod,
                                         project_name=self.project,
                                         case_name=self.case,
                                         installer=self.installer,
                                         version=self.version,
                                         start_date=self.start_date,
                                         stop_date=self.stop_date,
                                         details=self.details.format(),
                                         build_tag=self.build_tag,
                                         scenario=self.scenario,
                                         criteria=self.criteria,
                                         trust_indicator=self.trust_indicator)
        self.get_res = TestResult
        self.list_res = TestResults
        self.update_res = TestResult
        self.basePath = '/api/v1/results'
        self.req_pod = PodCreateRequest(self.pod, 'metal', 'zte pod 1')
        self.req_project = ProjectCreateRequest(self.project, 'vping test')
        self.req_testcase = TestcaseCreateRequest(self.case,
                                                  '/cases/vping',
                                                  'vping-ssh test')
        self.create_help('/api/v1/pods', self.req_pod)
        self.create_help('/api/v1/projects', self.req_project)
        self.create_help('/api/v1/projects/%s/cases',
                         self.req_testcase,
                         self.project)

    def assert_res(self, code, result, req=None):
        self.assertEqual(code, HTTP_OK)
        if req is None:
            req = self.req_d
        self.assertEqual(result.pod_name, req.pod_name)
        self.assertEqual(result.project_name, req.project_name)
        self.assertEqual(result.case_name, req.case_name)
        self.assertEqual(result.installer, req.installer)
        self.assertEqual(result.version, req.version)
        details_req = Details.from_dict(req.details)
        details_res = Details.from_dict(result.details)
        self.assertEqual(details_res.duration, details_req.duration)
        self.assertEqual(details_res.timestart, details_req.timestart)
        self.assertEqual(details_res.status, details_req.status)
        self.assertEqual(result.build_tag, req.build_tag)
        self.assertEqual(result.scenario, req.scenario)
        self.assertEqual(result.criteria, req.criteria)
        self.assertEqual(result.start_date, req.start_date)
        self.assertEqual(result.stop_date, req.stop_date)
        self.assertIsNotNone(result._id)
        ti = result.trust_indicator
        self.assertEqual(ti.current, req.trust_indicator.current)
        if ti.histories:
            history = ti.histories[0]
            self.assertEqual(history.date, self.update_date)
            self.assertEqual(history.step, self.update_step)

    def _create_d(self):
        _, res = self.create_d()
        return res.href.split('/')[-1]


class TestResultCreate(TestResultBase):
    def test_nobody(self):
        (code, body) = self.create(None)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('no body', body)

    def test_podNotProvided(self):
        req = self.req_d
        req.pod_name = None
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('pod_name missing', body)

    def test_projectNotProvided(self):
        req = self.req_d
        req.project_name = None
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('project_name missing', body)

    def test_testcaseNotProvided(self):
        req = self.req_d
        req.case_name = None
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('case_name missing', body)

    def test_noPod(self):
        req = self.req_d
        req.pod_name = 'notExistPod'
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_NOT_FOUND)
        self.assertIn('Could not find pod', body)

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

    def test_key_with_doc(self):
        req = copy.deepcopy(self.req_d)
        req.details = {'1.name': 'dot_name'}
        (code, body) = self.create(req)
        self.assertEqual(code, HTTP_OK)
        self.assert_href(body)

    def test_no_ti(self):
        req = ResultCreateRequest(pod_name=self.pod,
                                  project_name=self.project,
                                  case_name=self.case,
                                  installer=self.installer,
                                  version=self.version,
                                  start_date=self.start_date,
                                  stop_date=self.stop_date,
                                  details=self.details.format(),
                                  build_tag=self.build_tag,
                                  scenario=self.scenario,
                                  criteria=self.criteria)
        (code, res) = self.create(req)
        _id = res.href.split('/')[-1]
        self.assertEqual(code, HTTP_OK)
        code, body = self.get(_id)
        self.assert_res(code, body, req)


class TestResultGet(TestResultBase):
    def test_getOne(self):
        _id = self._create_d()
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

    def test_queryPeriodNotInt(self):
        code, body = self.query(self._set_query('period=a'))
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('period must be int', body)

    def test_queryPeriodFail(self):
        self._query_and_assert(self._set_query('period=1'),
                               found=False, days=-10)

    def test_queryPeriodSuccess(self):
        self._query_and_assert(self._set_query('period=1'),
                               found=True)

    def test_queryLastNotInt(self):
        code, body = self.query(self._set_query('last=a'))
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('last must be int', body)

    def test_queryLast(self):
        self._create_changed_date()
        req = self._create_changed_date(minutes=20)
        self._create_changed_date(minutes=-20)
        self._query_and_assert(self._set_query('last=1'), req=req)

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

    def _query_and_assert(self, query, found=True, req=None, **kwargs):
        if req is None:
            req = self._create_changed_date(**kwargs)
        code, body = self.query(query)
        if not found:
            self.assertEqual(code, HTTP_OK)
            self.assertEqual(0, len(body.results))
        else:
            self.assertEqual(1, len(body.results))
            for result in body.results:
                self.assert_res(code, result, req)

    def _create_changed_date(self, **kwargs):
        req = copy.deepcopy(self.req_d)
        req.start_date = datetime.now() + timedelta(**kwargs)
        req.stop_date = str(req.start_date + timedelta(minutes=10))
        req.start_date = str(req.start_date)
        self.create(req)
        return req

    def _set_query(self, *args):
        def get_value(arg):
            return self.__getattribute__(arg) \
                if arg != 'trust_indicator' else self.trust_indicator.current
        uri = ''
        for arg in args:
            if '=' in arg:
                uri += arg + '&'
            else:
                uri += '{}={}&'.format(arg, get_value(arg))
        return uri[0: -1]


class TestResultUpdate(TestResultBase):
    def test_success(self):
        _id = self._create_d()

        new_ti = copy.deepcopy(self.trust_indicator)
        new_ti.current += self.update_step
        new_ti.histories.append(TIHistory(self.update_date, self.update_step))
        new_data = copy.deepcopy(self.req_d)
        new_data.trust_indicator = new_ti
        update = ResultUpdateRequest(trust_indicator=new_ti)
        code, body = self.update(update, _id)
        self.assertEqual(_id, body._id)
        self.assert_res(code, body, new_data)

        code, new_body = self.get(_id)
        self.assertEqual(_id, new_body._id)
        self.assert_res(code, new_body, new_data)


if __name__ == '__main__':
    unittest.main()
