# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

import unittest

from tornado import web

import fake_pymongo
from opnfv_testapi.common import constants
from opnfv_testapi.resources import project_models
from opnfv_testapi.router import url_mappings
import test_base as base


class TestToken(base.TestBase):
    def get_app(self):
        return web.Application(
            url_mappings.mappings,
            db=fake_pymongo,
            debug=True,
            auth=True
        )


class TestTokenCreateProject(TestToken):
    def setUp(self):
        super(TestTokenCreateProject, self).setUp()
        self.req_d = project_models.ProjectCreateRequest('vping')
        fake_pymongo.tokens.insert({"access_token": "12345"})
        self.basePath = '/api/v1/projects'

    def test_projectCreateTokenInvalid(self):
        self.headers['X-Auth-Token'] = '1234'
        code, body = self.create_d()
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn('Invalid Token.', body)

    def test_projectCreateTokenUnauthorized(self):
        self.headers.pop('X-Auth-Token')
        code, body = self.create_d()
        self.assertEqual(code, constants.HTTP_UNAUTHORIZED)
        self.assertIn('No Authentication Header.', body)

    def test_projectCreateTokenSuccess(self):
        self.headers['X-Auth-Token'] = '12345'
        code, body = self.create_d()
        self.assertEqual(code, constants.HTTP_OK)


class TestTokenDeleteProject(TestToken):
    def setUp(self):
        super(TestTokenDeleteProject, self).setUp()
        self.req_d = project_models.ProjectCreateRequest('vping')
        fake_pymongo.tokens.insert({"access_token": "12345"})
        self.basePath = '/api/v1/projects'

    def test_projectDeleteTokenIvalid(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        self.headers['X-Auth-Token'] = '1234'
        code, body = self.delete(self.req_d.name)
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn('Invalid Token.', body)

    def test_projectDeleteTokenUnauthorized(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        self.headers.pop('X-Auth-Token')
        code, body = self.delete(self.req_d.name)
        self.assertEqual(code, constants.HTTP_UNAUTHORIZED)
        self.assertIn('No Authentication Header.', body)

    def test_projectDeleteTokenSuccess(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        code, body = self.delete(self.req_d.name)
        self.assertEqual(code, constants.HTTP_OK)


class TestTokenUpdateProject(TestToken):
    def setUp(self):
        super(TestTokenUpdateProject, self).setUp()
        self.req_d = project_models.ProjectCreateRequest('vping')
        fake_pymongo.tokens.insert({"access_token": "12345"})
        self.basePath = '/api/v1/projects'

    def test_projectUpdateTokenIvalid(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        code, body = self.get(self.req_d.name)
        self.headers['X-Auth-Token'] = '1234'
        req = project_models.ProjectUpdateRequest('newName', 'new description')
        code, body = self.update(req, self.req_d.name)
        self.assertEqual(code, constants.HTTP_FORBIDDEN)
        self.assertIn('Invalid Token.', body)

    def test_projectUpdateTokenUnauthorized(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        code, body = self.get(self.req_d.name)
        self.headers.pop('X-Auth-Token')
        req = project_models.ProjectUpdateRequest('newName', 'new description')
        code, body = self.update(req, self.req_d.name)
        self.assertEqual(code, constants.HTTP_UNAUTHORIZED)
        self.assertIn('No Authentication Header.', body)

    def test_projectUpdateTokenSuccess(self):
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()
        code, body = self.get(self.req_d.name)
        req = project_models.ProjectUpdateRequest('newName', 'new description')
        code, body = self.update(req, self.req_d.name)
        self.assertEqual(code, constants.HTTP_OK)

if __name__ == '__main__':
    unittest.main()
