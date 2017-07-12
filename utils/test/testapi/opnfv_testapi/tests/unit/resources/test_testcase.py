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

from opnfv_testapi.common import message
from opnfv_testapi.resources import project_models
from opnfv_testapi.resources import testcase_models
from opnfv_testapi.tests.unit import executor
from opnfv_testapi.tests.unit.resources import test_base as base


class TestCaseBase(base.TestBase):
    def setUp(self):
        super(TestCaseBase, self).setUp()
        self.req_d = testcase_models.TestcaseCreateRequest('vping_1',
                                                           '/cases/vping_1',
                                                           'vping-ssh test')
        self.req_e = testcase_models.TestcaseCreateRequest('doctor_1',
                                                           '/cases/doctor_1',
                                                           'create doctor')
        self.update_d = testcase_models.TestcaseUpdateRequest('vping_1',
                                                              'vping-ssh test',
                                                              'functest')
        self.update_e = testcase_models.TestcaseUpdateRequest('doctor_1',
                                                              'create doctor',
                                                              'functest')
        self.get_res = testcase_models.Testcase
        self.list_res = testcase_models.Testcases
        self.update_res = testcase_models.Testcase
        self.basePath = '/api/v1/projects/%s/cases'
        self.create_project()

    def assert_body(self, case, req=None):
        if not req:
            req = self.req_d
        self.assertEqual(case.name, req.name)
        self.assertEqual(case.description, req.description)
        self.assertEqual(case.url, req.url)
        self.assertIsNotNone(case._id)
        self.assertIsNotNone(case.creation_date)

    def assert_update_body(self, old, new, req=None):
        if not req:
            req = self.req_d
        self.assertEqual(new.name, req.name)
        self.assertEqual(new.description, req.description)
        self.assertEqual(new.url, old.url)
        self.assertIsNotNone(new._id)
        self.assertIsNotNone(new.creation_date)

    def create_project(self):
        req_p = project_models.ProjectCreateRequest('functest',
                                                    'vping-ssh test')
        self.create_help('/api/v1/projects', req_p)
        self.project = req_p.name

    def create_d(self):
        return super(TestCaseBase, self).create_d(self.project)

    def create_e(self):
        return super(TestCaseBase, self).create_e(self.project)

    def get(self, case=None):
        return super(TestCaseBase, self).get(self.project, case)

    def create(self, req=None, *args):
        return super(TestCaseBase, self).create(req, self.project)

    def update(self, new=None, case=None):
        return super(TestCaseBase, self).update(new, self.project, case)

    def delete(self, case):
        return super(TestCaseBase, self).delete(self.project, case)


class TestCaseCreate(TestCaseBase):
    @executor.create(httplib.BAD_REQUEST, message.no_body())
    def test_noBody(self):
        return None

    @executor.create(httplib.FORBIDDEN, message.not_found_base)
    def test_noProject(self):
        self.project = 'noProject'
        return self.req_d

    @executor.create(httplib.BAD_REQUEST, message.missing('name'))
    def test_emptyName(self):
        req_empty = testcase_models.TestcaseCreateRequest('')
        return req_empty

    @executor.create(httplib.BAD_REQUEST, message.missing('name'))
    def test_noneName(self):
        req_none = testcase_models.TestcaseCreateRequest(None)
        return req_none

    @executor.create(httplib.OK, '_assert_success')
    def test_success(self):
        return self.req_d

    def _assert_success(self, body):
        self.assert_create_body(body, self.req_d, self.project)

    @executor.create(httplib.FORBIDDEN, message.exist_base)
    def test_alreadyExist(self):
        self.create_d()
        return self.req_d


class TestCaseGet(TestCaseBase):
    def setUp(self):
        super(TestCaseGet, self).setUp()
        self.create_d()
        self.create_e()

    @executor.get(httplib.NOT_FOUND, message.not_found_base)
    def test_notExist(self):
        return 'notExist'

    @executor.get(httplib.OK, 'assert_body')
    def test_getOne(self):
        return self.req_d.name

    @executor.get(httplib.OK, '_list')
    def test_list(self):
        return None

    def _list(self, body):
        for case in body.testcases:
            if self.req_d.name == case.name:
                self.assert_body(case)
            else:
                self.assert_body(case, self.req_e)


class TestCaseUpdate(TestCaseBase):
    def setUp(self):
        super(TestCaseUpdate, self).setUp()
        self.create_d()

    @executor.update(httplib.BAD_REQUEST, message.no_body())
    def test_noBody(self):
        return None, 'noBody'

    @executor.update(httplib.NOT_FOUND, message.not_found_base)
    def test_notFound(self):
        return self.update_e, 'notFound'

    @executor.update(httplib.FORBIDDEN, message.exist_base)
    def test_newNameExist(self):
        self.create_e()
        return self.update_e, self.req_d.name

    @executor.update(httplib.FORBIDDEN, message.no_update())
    def test_noUpdate(self):
        return self.update_d, self.req_d.name

    @executor.update(httplib.OK, '_update_success')
    def test_success(self):
        return self.update_e, self.req_d.name

    @executor.update(httplib.OK, '_update_success')
    def test_with_dollar(self):
        update = copy.deepcopy(self.update_d)
        update.description = {'2. change': 'dollar change'}
        return update, self.req_d.name

    def _update_success(self, request, body):
        self.assert_update_body(self.req_d, body, request)
        _, new_body = self.get(request.name)
        self.assert_update_body(self.req_d, new_body, request)


class TestCaseDelete(TestCaseBase):
    def setUp(self):
        super(TestCaseDelete, self).setUp()
        self.create_d()

    @executor.delete(httplib.NOT_FOUND, message.not_found_base)
    def test_notFound(self):
        return 'notFound'

    @executor.delete(httplib.OK, '_delete_success')
    def test_success(self):
        return self.req_d.name

    def _delete_success(self, body):
        self.assertEqual(body, '')
        code, body = self.get(self.req_d.name)
        self.assertEqual(code, httplib.NOT_FOUND)


if __name__ == '__main__':
    unittest.main()
