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

from opnfv_testapi.common import constants
from opnfv_testapi.resources import project_models
from opnfv_testapi.resources import testcase_models
import test_base as base


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

    def update(self, new=None, case=None):
        return super(TestCaseBase, self).update(new, self.project, case)

    def delete(self, case):
        return super(TestCaseBase, self).delete(self.project, case)


class TestCaseCreate(TestCaseBase):
    def test_noBody(self):
        (code, body) = self.create(None, 'vping')
        self.assertEqual(code, constants.HTTP_BAD_REQUEST)

    def test_noProject(self):
        code, body = self.create(self.req_d, 'noProject')
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn('Could not find project', body)

    def test_emptyName(self):
        req_empty = testcase_models.TestcaseCreateRequest('')
        (code, body) = self.create(req_empty, self.project)
        self.assertEqual(code, constants.HTTP_BAD_REQUEST)
        self.assertIn('name missing', body)

    def test_noneName(self):
        req_none = testcase_models.TestcaseCreateRequest(None)
        (code, body) = self.create(req_none, self.project)
        self.assertEqual(code, constants.HTTP_BAD_REQUEST)
        self.assertIn('name missing', body)

    def test_success(self):
        code, body = self.create_d()
        self.assertEqual(code, constants.HTTP_OK)
        self.assert_create_body(body, None, self.project)

    def test_alreadyExist(self):
        self.create_d()
        code, body = self.create_d()
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn('already exists', body)


class TestCaseGet(TestCaseBase):
    def test_notExist(self):
        code, body = self.get('notExist')
        self.assertEqual(code, constants.HTTP_NOT_FOUND)

    def test_getOne(self):
        self.create_d()
        code, body = self.get(self.req_d.name)
        self.assertEqual(code, constants.HTTP_OK)
        self.assert_body(body)

    def test_list(self):
        self.create_d()
        self.create_e()
        code, body = self.get()
        for case in body.testcases:
            if self.req_d.name == case.name:
                self.assert_body(case)
            else:
                self.assert_body(case, self.req_e)


class TestCaseUpdate(TestCaseBase):
    def test_noBody(self):
        code, _ = self.update(case='noBody')
        self.assertEqual(code, constants.HTTP_BAD_REQUEST)

    def test_notFound(self):
        code, _ = self.update(self.update_e, 'notFound')
        self.assertEqual(code, constants.HTTP_NOT_FOUND)

    def test_newNameExist(self):
        self.create_d()
        self.create_e()
        code, body = self.update(self.update_e, self.req_d.name)
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn("already exists", body)

    def test_noUpdate(self):
        self.create_d()
        code, body = self.update(self.update_d, self.req_d.name)
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn("Nothing to update", body)

    def test_success(self):
        self.create_d()
        code, body = self.get(self.req_d.name)
        _id = body._id

        code, body = self.update(self.update_e, self.req_d.name)
        self.assertEqual(code, constants.HTTP_OK)
        self.assertEqual(_id, body._id)
        self.assert_update_body(self.req_d, body, self.update_e)

        _, new_body = self.get(self.req_e.name)
        self.assertEqual(_id, new_body._id)
        self.assert_update_body(self.req_d, new_body, self.update_e)

    def test_with_dollar(self):
        self.create_d()
        update = copy.deepcopy(self.update_d)
        update.description = {'2. change': 'dollar change'}
        code, body = self.update(update, self.req_d.name)
        self.assertEqual(code, constants.HTTP_OK)


class TestCaseDelete(TestCaseBase):
    def test_notFound(self):
        code, body = self.delete('notFound')
        self.assertEqual(code, constants.HTTP_NOT_FOUND)

    def test_success(self):
        self.create_d()
        code, body = self.delete(self.req_d.name)
        self.assertEqual(code, constants.HTTP_OK)
        self.assertEqual(body, '')

        code, body = self.get(self.req_d.name)
        self.assertEqual(code, constants.HTTP_NOT_FOUND)


if __name__ == '__main__':
    unittest.main()
