# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

import unittest

from tornado.web import Application
from opnfv_testapi.router import url_mappings
import fake_pymongo

from test_base import TestBase
from opnfv_testapi.resources.project_models import ProjectCreateRequest, \
    ProjectUpdateRequest
from opnfv_testapi.common.constants import HTTP_FORBIDDEN, HTTP_UNAUTHORIZED, \
    HTTP_OK

class TestToken(TestBase):
    def get_app(self):
        return Application(
            url_mappings.mappings,
            db=fake_pymongo,
            debug=True,
            auth=True
        )

class TestTokenCreateProject(TestToken):
    def setUp(self):
        super(TestTokenCreateProject, self).setUp()
        self.req_d = ProjectCreateRequest('vping')
        fake_pymongo.tokens.insert({"access_token":"12345"})
        self.basePath = '/api/v1/projects'

    def test_projectCreateTokenInvalid(self):
        self.headers['X-Auth-Token'] = '1234'
        code, body = self.create_d()
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn('Invalid Token.', body)

    def test_projectCreateTokenUnauthorized(self):
        self.headers.pop('X-Auth-Token')
        code, body = self.create_d()
        self.assertEqual(code, HTTP_UNAUTHORIZED)
        self.assertIn('No Authentication Header.', body)

    def test_projectCreateTokenSuccess(self):
        self.headers['X-Auth-Token'] = '12345'
        code, body = self.create_d()
        self.assertEqual(code, 200)

class TestTokenDeleteProject(TestToken):
    def setUp(self):
        super(TestTokenDeleteProject, self).setUp()
        self.req_d = ProjectCreateRequest('vping')
        fake_pymongo.tokens.insert({"access_token":"12345"})
        self.basePath = '/api/v1/projects'

    def test_projectDeleteTokenIvalid(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        self.headers['X-Auth-Token'] = '1234'
        code, body = self.delete(self.req_d.name)
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn('Invalid Token.', body)

    def test_projectDeleteTokenUnauthorized(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        self.headers.pop('X-Auth-Token')
        code, body = self.delete(self.req_d.name)
        self.assertEqual(code, HTTP_UNAUTHORIZED)
        self.assertIn('No Authentication Header.', body)

    def test_projectDeleteTokenSuccess(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        code, body = self.delete(self.req_d.name)
        self.assertEqual(code, 200)

class TestTokenUpdateProject(TestToken):
    def setUp(self):
        super(TestTokenUpdateProject, self).setUp()
        self.req_d = ProjectCreateRequest('vping')
        fake_pymongo.tokens.insert({"access_token":"12345"})
        self.basePath = '/api/v1/projects'

    def test_projectUpdateTokenIvalid(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        code, body = self.get(self.req_d.name)
        self.headers['X-Auth-Token'] = '1234'
        req = ProjectUpdateRequest('newName', 'new description')
        code, body = self.update(req, self.req_d.name)
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn('Invalid Token.', body)

    def test_projectUpdateTokenUnauthorized(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        code, body = self.get(self.req_d.name)
        self.headers.pop('X-Auth-Token')
        req = ProjectUpdateRequest('newName', 'new description')
        code, body = self.update(req, self.req_d.name)
        self.assertEqual(code, HTTP_UNAUTHORIZED)
        self.assertIn('No Authentication Header.', body)

    def test_projectUpdateTokenSuccess(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        code, body = self.get(self.req_d.name)
        req = ProjectUpdateRequest('newName', 'new description')
        code, body = self.update(req, self.req_d.name)
        self.assertEqual(code, 200)

if __name__ == '__main__':
    unittest.main()
