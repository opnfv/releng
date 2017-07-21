##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import copy
import httplib
import unittest
from datetime import datetime, timedelta
import json

from opnfv_testapi.common import message
from opnfv_testapi.resources import pod_models
from opnfv_testapi.resources import project_models
from opnfv_testapi.resources import result_models
from opnfv_testapi.resources import testcase_models
from opnfv_testapi.tests.unit import executor
from opnfv_testapi.tests.unit.resources import test_base as base


class Details(object):
    def __init__(self, timestart=None, duration=None, status=None):
        self.timestart = timestart
        self.duration = duration
        self.status = status
        self.items = [{'item1': 1}, {'item2': 2}]

    def format(self):
        return {
            "timestart": self.timestart,
            "duration": self.duration,
            "status": self.status,
            'items': [{'item1': 1}, {'item2': 2}]
        }

    @staticmethod
    def from_dict(a_dict):

        if a_dict is None:
            return None

        t = Details()
        t.timestart = a_dict.get('timestart')
        t.duration = a_dict.get('duration')
        t.status = a_dict.get('status')
        t.items = a_dict.get('items')
        return t


class TestResultBase(base.TestBase):
    def setUp(self):
        self.pod = 'zte-pod1'
        self.project = 'functest'
        self.case = 'vPing'
        self.installer = 'fuel'
        self.version = 'C'
        self.build_tag = 'v3.0'
        self.scenario = 'odl-l2'
        self.criteria = 'passed'
        self.trust_indicator = result_models.TI(0.7)
        self.start_date = str(datetime.now())
        self.stop_date = str(datetime.now() + timedelta(minutes=1))
        self.update_date = str(datetime.now() + timedelta(days=1))
        self.update_step = -0.05
        super(TestResultBase, self).setUp()
        self.details = Details(timestart='0', duration='9s', status='OK')
        self.req_d = result_models.ResultCreateRequest(
            pod_name=self.pod,
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
        self.get_res = result_models.TestResult
        self.list_res = result_models.TestResults
        self.update_res = result_models.TestResult
        self.basePath = '/api/v1/results'
        self.req_pod = pod_models.PodCreateRequest(
            self.pod,
            'metal',
            'zte pod 1')
        self.req_project = project_models.ProjectCreateRequest(
            self.project,
            'vping test')
        self.req_testcase = testcase_models.TestcaseCreateRequest(
            self.case,
            '/cases/vping',
            'vping-ssh test')
        self.create_help('/api/v1/pods', self.req_pod)
        self.create_help('/api/v1/projects', self.req_project)
        self.create_help('/api/v1/projects/%s/cases',
                         self.req_testcase,
                         self.project)

    def assert_res(self, result, req=None):
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
        self.assertEqual(details_res.items, details_req.items)
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

    def upload(self, req):
        if req and not isinstance(req, str) and hasattr(req, 'format'):
            req = req.format()
        res = self.fetch(self.basePath + '/upload',
                         method='POST',
                         body=json.dumps(req),
                         headers=self.headers)

        return self._get_return(res, self.create_res)


class TestResultUpload(TestResultBase):
    @executor.upload(httplib.BAD_REQUEST, message.key_error('file'))
    def test_filenotfind(self):
        return None


class TestResultCreate(TestResultBase):
    @executor.create(httplib.BAD_REQUEST, message.no_body())
    def test_nobody(self):
        return None

    @executor.create(httplib.BAD_REQUEST, message.missing('pod_name'))
    def test_podNotProvided(self):
        req = self.req_d
        req.pod_name = None
        return req

    @executor.create(httplib.BAD_REQUEST, message.missing('project_name'))
    def test_projectNotProvided(self):
        req = self.req_d
        req.project_name = None
        return req

    @executor.create(httplib.BAD_REQUEST, message.missing('case_name'))
    def test_testcaseNotProvided(self):
        req = self.req_d
        req.case_name = None
        return req

    @executor.create(httplib.FORBIDDEN, message.not_found_base)
    def test_noPod(self):
        req = self.req_d
        req.pod_name = 'notExistPod'
        return req

    @executor.create(httplib.FORBIDDEN, message.not_found_base)
    def test_noProject(self):
        req = self.req_d
        req.project_name = 'notExistProject'
        return req

    @executor.create(httplib.FORBIDDEN, message.not_found_base)
    def test_noTestcase(self):
        req = self.req_d
        req.case_name = 'notExistTestcase'
        return req

    @executor.create(httplib.OK, 'assert_href')
    def test_success(self):
        return self.req_d

    @executor.create(httplib.OK, 'assert_href')
    def test_key_with_doc(self):
        req = copy.deepcopy(self.req_d)
        req.details = {'1.name': 'dot_name'}
        return req

    @executor.create(httplib.OK, '_assert_no_ti')
    def test_no_ti(self):
        req = result_models.ResultCreateRequest(pod_name=self.pod,
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
        self.actual_req = req
        return req

    def _assert_no_ti(self, body):
        _id = body.href.split('/')[-1]
        code, body = self.get(_id)
        self.assert_res(body, self.actual_req)


class TestResultGet(TestResultBase):
    def setUp(self):
        super(TestResultGet, self).setUp()
        self.req_10d_before = self._create_changed_date(days=-10)
        self.req_d_id = self._create_d()
        self.req_10d_later = self._create_changed_date(days=10)

    @executor.get(httplib.OK, 'assert_res')
    def test_getOne(self):
        return self.req_d_id

    @executor.query(httplib.OK, '_query_success', 3)
    def test_queryPod(self):
        return self._set_query('pod')

    @executor.query(httplib.OK, '_query_success', 3)
    def test_queryProject(self):
        return self._set_query('project')

    @executor.query(httplib.OK, '_query_success', 3)
    def test_queryTestcase(self):
        return self._set_query('case')

    @executor.query(httplib.OK, '_query_success', 3)
    def test_queryVersion(self):
        return self._set_query('version')

    @executor.query(httplib.OK, '_query_success', 3)
    def test_queryInstaller(self):
        return self._set_query('installer')

    @executor.query(httplib.OK, '_query_success', 3)
    def test_queryBuildTag(self):
        return self._set_query('build_tag')

    @executor.query(httplib.OK, '_query_success', 3)
    def test_queryScenario(self):
        return self._set_query('scenario')

    @executor.query(httplib.OK, '_query_success', 3)
    def test_queryTrustIndicator(self):
        return self._set_query('trust_indicator')

    @executor.query(httplib.OK, '_query_success', 3)
    def test_queryCriteria(self):
        return self._set_query('criteria')

    @executor.query(httplib.BAD_REQUEST, message.must_int('period'))
    def test_queryPeriodNotInt(self):
        return self._set_query('period=a')

    @executor.query(httplib.OK, '_query_period_one', 1)
    def test_queryPeriodSuccess(self):
        return self._set_query('period=5')

    @executor.query(httplib.BAD_REQUEST, message.must_int('last'))
    def test_queryLastNotInt(self):
        return self._set_query('last=a')

    @executor.query(httplib.OK, '_query_last_one', 1)
    def test_queryLast(self):
        return self._set_query('last=1')

    @executor.query(httplib.OK, '_query_success', 4)
    def test_queryPublic(self):
        self._create_public_data()
        return self._set_query('')

    @executor.query(httplib.OK, '_query_success', 1)
    def test_queryPrivate(self):
        self._create_private_data()
        return self._set_query('public=false')

    @executor.query(httplib.OK, '_query_period_one', 1)
    def test_combination(self):
        return self._set_query('pod',
                               'project',
                               'case',
                               'version',
                               'installer',
                               'build_tag',
                               'scenario',
                               'trust_indicator',
                               'criteria',
                               'period=5')

    @executor.query(httplib.OK, '_query_success', 0)
    def test_notFound(self):
        return self._set_query('pod=notExistPod',
                               'project',
                               'case',
                               'version',
                               'installer',
                               'build_tag',
                               'scenario',
                               'trust_indicator',
                               'criteria',
                               'period=1')

    @executor.query(httplib.OK, '_query_success', 1)
    def test_filterErrorStartdate(self):
        self._create_error_start_date(None)
        self._create_error_start_date('None')
        self._create_error_start_date('null')
        self._create_error_start_date('')
        return self._set_query('period=5')

    def _query_success(self, body, number):
        self.assertEqual(number, len(body.results))

    def _query_last_one(self, body, number):
        self.assertEqual(number, len(body.results))
        self.assert_res(body.results[0], self.req_10d_later)

    def _query_period_one(self, body, number):
        self.assertEqual(number, len(body.results))
        self.assert_res(body.results[0], self.req_d)

    def _create_error_start_date(self, start_date):
        req = copy.deepcopy(self.req_d)
        req.start_date = start_date
        self.create(req)
        return req

    def _create_changed_date(self, **kwargs):
        req = copy.deepcopy(self.req_d)
        req.start_date = datetime.now() + timedelta(**kwargs)
        req.stop_date = str(req.start_date + timedelta(minutes=10))
        req.start_date = str(req.start_date)
        self.create(req)
        return req

    def _create_public_data(self, **kwargs):
        req = copy.deepcopy(self.req_d)
        req.public = 'true'
        self.create(req)
        return req

    def _create_private_data(self, **kwargs):
        req = copy.deepcopy(self.req_d)
        req.public = 'false'
        self.create(req)
        return req

    def _set_query(self, *args):
        def get_value(arg):
            return self.__getattribute__(arg) \
                if arg != 'trust_indicator' else self.trust_indicator.current
        uri = ''
        for arg in args:
            if arg:
                if '=' in arg:
                    uri += arg + '&'
                else:
                    uri += '{}={}&'.format(arg, get_value(arg))
        return uri[0: -1]


class TestResultUpdate(TestResultBase):
    def setUp(self):
        super(TestResultUpdate, self).setUp()
        self.req_d_id = self._create_d()

    @executor.update(httplib.OK, '_assert_update_ti')
    def test_success(self):
        new_ti = copy.deepcopy(self.trust_indicator)
        new_ti.current += self.update_step
        new_ti.histories.append(
            result_models.TIHistory(self.update_date, self.update_step))
        new_data = copy.deepcopy(self.req_d)
        new_data.trust_indicator = new_ti
        update = result_models.ResultUpdateRequest(trust_indicator=new_ti)
        self.update_req = new_data
        return update, self.req_d_id

    def _assert_update_ti(self, request, body):
        ti = body.trust_indicator
        self.assertEqual(ti.current, request.trust_indicator.current)
        if ti.histories:
            history = ti.histories[0]
            self.assertEqual(history.date, self.update_date)
            self.assertEqual(history.step, self.update_step)


if __name__ == '__main__':
    unittest.main()
