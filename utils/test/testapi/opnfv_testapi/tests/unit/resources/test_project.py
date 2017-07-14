import httplib
import unittest

from opnfv_testapi.common import message
from opnfv_testapi.resources import project_models
from opnfv_testapi.tests.unit import executor
from opnfv_testapi.tests.unit.resources import test_base as base


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
    @executor.create(httplib.BAD_REQUEST, message.no_body())
    def test_withoutBody(self):
        return None

    @executor.create(httplib.BAD_REQUEST, message.missing('name'))
    def test_emptyName(self):
        return project_models.ProjectCreateRequest('')

    @executor.create(httplib.BAD_REQUEST, message.missing('name'))
    def test_noneName(self):
        return project_models.ProjectCreateRequest(None)

    @executor.create(httplib.OK, 'assert_create_body')
    def test_success(self):
        return self.req_d

    @executor.create(httplib.FORBIDDEN, message.exist_base)
    def test_alreadyExist(self):
        self.create_d()
        return self.req_d


class TestProjectGet(TestProjectBase):
    def setUp(self):
        super(TestProjectGet, self).setUp()
        self.create_d()
        self.create_e()

    @executor.get(httplib.NOT_FOUND, message.not_found_base)
    def test_notExist(self):
        return 'notExist'

    @executor.get(httplib.OK, 'assert_body')
    def test_getOne(self):
        return self.req_d.name

    @executor.get(httplib.OK, '_assert_list')
    def test_list(self):
        return None

    def _assert_list(self, body):
        for project in body.projects:
            if self.req_d.name == project.name:
                self.assert_body(project)
            else:
                self.assert_body(project, self.req_e)


class TestProjectUpdate(TestProjectBase):
    def setUp(self):
        super(TestProjectUpdate, self).setUp()
        _, d_body = self.create_d()
        _, get_res = self.get(self.req_d.name)
        self.index_d = get_res._id
        self.create_e()

    @executor.update(httplib.BAD_REQUEST, message.no_body())
    def test_withoutBody(self):
        return None, 'noBody'

    @executor.update(httplib.NOT_FOUND, message.not_found_base)
    def test_notFound(self):
        return self.req_e, 'notFound'

    @executor.update(httplib.FORBIDDEN, message.exist_base)
    def test_newNameExist(self):
        return self.req_e, self.req_d.name

    @executor.update(httplib.FORBIDDEN, message.no_update())
    def test_noUpdate(self):
        return self.req_d, self.req_d.name

    @executor.update(httplib.OK, '_assert_update')
    def test_success(self):
        req = project_models.ProjectUpdateRequest('newName', 'new description')
        return req, self.req_d.name

    def _assert_update(self, req, body):
        self.assertEqual(self.index_d, body._id)
        self.assert_body(body, req)
        _, new_body = self.get(req.name)
        self.assertEqual(self.index_d, new_body._id)
        self.assert_body(new_body, req)


class TestProjectDelete(TestProjectBase):
    def setUp(self):
        super(TestProjectDelete, self).setUp()
        self.create_d()

    @executor.delete(httplib.NOT_FOUND, message.not_found_base)
    def test_notFound(self):
        return 'notFound'

    @executor.delete(httplib.OK, '_assert_delete')
    def test_success(self):
        return self.req_d.name

    def _assert_delete(self, body):
        self.assertEqual(body, '')
        code, body = self.get(self.req_d.name)
        self.assertEqual(code, httplib.NOT_FOUND)


if __name__ == '__main__':
    unittest.main()
