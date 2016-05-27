import unittest

from test_base import TestBase
from resources.testcase_models import TestcaseCreateRequest, \
    Testcase, Testcases, TestcaseUpdateRequest
from resources.project_models import ProjectCreateRequest
from common.constants import HTTP_OK, HTTP_BAD_REQUEST, \
    HTTP_FORBIDDEN, HTTP_NOT_FOUND


__author__ = '__serena__'


class TestCaseBase(TestBase):
    def setUp(self):
        super(TestCaseBase, self).setUp()
        self.req_d = TestcaseCreateRequest('vping_1',
                                           '/cases/vping_1',
                                           'vping-ssh test')
        self.req_e = TestcaseCreateRequest('doctor_1',
                                           '/cases/doctor_1',
                                           'create doctor')
        self.update_d = TestcaseUpdateRequest('vping_1',
                                              'vping-ssh test',
                                              'functest')
        self.update_e = TestcaseUpdateRequest('doctor_1',
                                              'create doctor',
                                              'functest')
        self.get_res = Testcase
        self.list_res = Testcases
        self.update_res = Testcase
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
        req_p = ProjectCreateRequest('functest', 'vping-ssh test')
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
        self.assertEqual(code, HTTP_BAD_REQUEST)

    def test_noProject(self):
        code, body = self.create(self.req_d, 'noProject')
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn('Could not find project', body)

    def test_emptyName(self):
        req_empty = TestcaseCreateRequest('')
        (code, body) = self.create(req_empty, self.project)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('testcase name missing', body)

    def test_noneName(self):
        req_none = TestcaseCreateRequest(None)
        (code, body) = self.create(req_none, self.project)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('testcase name missing', body)

    def test_success(self):
        code, body = self.create_d()
        self.assertEqual(code, HTTP_OK)
        self.assert_create_body(body, None, self.project)

    def test_alreadyExist(self):
        self.create_d()
        code, body = self.create_d()
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn('already exists', body)


class TestCaseGet(TestCaseBase):
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
        for case in body.testcases:
            if self.req_d.name == case.name:
                self.assert_body(case)
            else:
                self.assert_body(case, self.req_e)


class TestCaseUpdate(TestCaseBase):
    def test_noBody(self):
        code, _ = self.update(case='noBody')
        self.assertEqual(code, HTTP_BAD_REQUEST)

    def test_notFound(self):
        code, _ = self.update(self.update_e, 'notFound')
        self.assertEqual(code, HTTP_NOT_FOUND)

    def test_newNameExist(self):
        self.create_d()
        self.create_e()
        code, body = self.update(self.update_e, self.req_d.name)
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn("already exists", body)

    def test_noUpdate(self):
        self.create_d()
        code, body = self.update(self.update_d, self.req_d.name)
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn("Nothing to update", body)

    def test_success(self):
        self.create_d()
        code, body = self.get(self.req_d.name)
        _id = body._id

        code, body = self.update(self.update_e, self.req_d.name)
        self.assertEqual(code, HTTP_OK)
        self.assertEqual(_id, body._id)
        self.assert_update_body(self.req_d, body, self.update_e)

        _, new_body = self.get(self.req_e.name)
        self.assertEqual(_id, new_body._id)
        self.assert_update_body(self.req_d, new_body, self.update_e)


class TestCaseDelete(TestCaseBase):
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
