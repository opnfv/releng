import unittest

from test_base import TestBase
from resources.project_models import ProjectCreateRequest, Project, Projects
from common.constants import HTTP_OK, HTTP_BAD_REQUEST, \
    HTTP_FORBIDDEN, HTTP_NOT_FOUND


class TestProjectBase(TestBase):
    def setUp(self):
        super(TestProjectBase, self).setUp()
        self.req_d = ProjectCreateRequest('vping', 'vping-ssh test')
        self.req_e = ProjectCreateRequest('doctor', 'doctor test')
        self.get_res = Project
        self.list_res = Projects
        self.update_res = Project
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
        self.assertEqual(code, HTTP_BAD_REQUEST)

    def test_emptyName(self):
        req_empty = ProjectCreateRequest('')
        (code, body) = self.create(req_empty)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('name missing', body)

    def test_noneName(self):
        req_none = ProjectCreateRequest(None)
        (code, body) = self.create(req_none)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('name missing', body)

    def test_success(self):
        (code, body) = self.create_d()
        self.assertEqual(code, HTTP_OK)
        self.assert_create_body(body)

    def test_alreadyExist(self):
        self.create_d()
        (code, body) = self.create_d()
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn('already exists', body)


class TestProjectGet(TestProjectBase):
    def test_notExist(self):
        code, body = self.get('notExist')
        self.assertEqual(code, HTTP_NOT_FOUND)

    def test_getOne(self):
        self.create_d()
        code, body = self.get(self.req_d.name)
        self.assertEqual(code, HTTP_OK)
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
        self.assertEqual(code, HTTP_BAD_REQUEST)

    def test_notFound(self):
        code, _ = self.update(self.req_e, 'notFound')
        self.assertEqual(code, HTTP_NOT_FOUND)

    def test_newNameExist(self):
        self.create_d()
        self.create_e()
        code, body = self.update(self.req_e, self.req_d.name)
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn("already exists", body)

    def test_noUpdate(self):
        self.create_d()
        code, body = self.update(self.req_d, self.req_d.name)
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn("Nothing to update", body)

    def test_success(self):
        self.create_d()
        code, body = self.get(self.req_d.name)
        _id = body._id

        req = ProjectCreateRequest('newName', 'new description')
        code, body = self.update(req, self.req_d.name)
        self.assertEqual(code, HTTP_OK)
        self.assertEqual(_id, body._id)
        self.assert_body(body, req)

        _, new_body = self.get(req.name)
        self.assertEqual(_id, new_body._id)
        self.assert_body(new_body, req)


class TestProjectDelete(TestProjectBase):
    def test_notFound(self):
        code, body = self.delete('notFound')
        self.assertEqual(code, HTTP_NOT_FOUND)

    def test_success(self):
        self.create_d()
        code, body = self.delete(self.req_d.name)
        self.assertEqual(code, HTTP_OK)
        self.assertEqual(body, '')

        code, body = self.get(self.req_d.name)
        self.assertEqual(code, HTTP_NOT_FOUND)

if __name__ == '__main__':
    unittest.main()
