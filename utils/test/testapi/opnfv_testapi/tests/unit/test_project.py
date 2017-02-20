##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import unittest

from opnfv_testapi.common import constants
from opnfv_testapi.resources import project_models
import test_base as base


class TestProjectBase(base.TestBase):
    def setUp(self):
        super(TestProjectBase, self).setUp()
        self.req_d = project_models.ProjectCreateRequest('vping',
                                                         'vping-ssh test')
        self.req_e = project_models.ProjectCreateRequest('doctor',
                                                         'doctor test')
        self.get_res = project_models.Project
        self.list_res = project_models.Projects
        self.update_res = project_models.Project
        self.basePath = '/api/v1/projects'

    def assert_body(self, project, req=None):
        if not req:
            req = self.req_d
        self.assertEqual(project.name, req.name)
        self.assertEqual(project.description, req.description)
        self.assertIsNotNone(project._id)
        self.assertIsNotNone(project.creation_date)


class TestProjectCreate(TestProjectBase):
    def test_withoutBody(self):
        (code, body) = self.create()
        self.assertEqual(code, constants.HTTP_BAD_REQUEST)

    def test_emptyName(self):
        req_empty = project_models.ProjectCreateRequest('')
        (code, body) = self.create(req_empty)
        self.assertEqual(code, constants.HTTP_BAD_REQUEST)
        self.assertIn('name missing', body)

    def test_noneName(self):
        req_none = project_models.ProjectCreateRequest(None)
        (code, body) = self.create(req_none)
        self.assertEqual(code, constants.HTTP_BAD_REQUEST)
        self.assertIn('name missing', body)

    def test_success(self):
        (code, body) = self.create_d()
        self.assertEqual(code, constants.HTTP_OK)
        self.assert_create_body(body)

    def test_alreadyExist(self):
        self.create_d()
        (code, body) = self.create_d()
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn('already exists', body)


class TestProjectGet(TestProjectBase):
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
        for project in body.projects:
            if self.req_d.name == project.name:
                self.assert_body(project)
            else:
                self.assert_body(project, self.req_e)


class TestProjectUpdate(TestProjectBase):
    def test_withoutBody(self):
        code, _ = self.update(None, 'noBody')
        self.assertEqual(code, constants.HTTP_BAD_REQUEST)

    def test_notFound(self):
        code, _ = self.update(self.req_e, 'notFound')
        self.assertEqual(code, constants.HTTP_NOT_FOUND)

    def test_newNameExist(self):
        self.create_d()
        self.create_e()
        code, body = self.update(self.req_e, self.req_d.name)
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn("already exists", body)

    def test_noUpdate(self):
        self.create_d()
        code, body = self.update(self.req_d, self.req_d.name)
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn("Nothing to update", body)

    def test_success(self):
        self.create_d()
        code, body = self.get(self.req_d.name)
        _id = body._id

        req = project_models.ProjectUpdateRequest('newName', 'new description')
        code, body = self.update(req, self.req_d.name)
        self.assertEqual(code, constants.HTTP_OK)
        self.assertEqual(_id, body._id)
        self.assert_body(body, req)

        _, new_body = self.get(req.name)
        self.assertEqual(_id, new_body._id)
        self.assert_body(new_body, req)


class TestProjectDelete(TestProjectBase):
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
