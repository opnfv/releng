# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

import httplib
import unittest

from tornado import web

from opnfv_testapi.common import message
from opnfv_testapi.resources import project_models
from opnfv_testapi.tests.unit import executor
from opnfv_testapi.tests.unit import fake_pymongo
from opnfv_testapi.tests.unit.resources import test_base as base


class TestToken(base.TestBase):
    def get_app(self):
        from opnfv_testapi.router import url_mappings
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

    @executor.create(httplib.FORBIDDEN, message.invalid_token())
    def test_projectCreateTokenInvalid(self):
        self.headers['X-Auth-Token'] = '1234'
        return self.req_d

    @executor.create(httplib.UNAUTHORIZED, message.unauthorized())
    def test_projectCreateTokenUnauthorized(self):
        if 'X-Auth-Token' in self.headers:
            self.headers.pop('X-Auth-Token')
        return self.req_d

    @executor.create(httplib.OK, '_create_success')
    def test_projectCreateTokenSuccess(self):
        self.headers['X-Auth-Token'] = '12345'
        return self.req_d

    def _create_success(self, body):
        self.assertIn('CreateResponse', str(type(body)))


class TestTokenDeleteProject(TestToken):
    def setUp(self):
        super(TestTokenDeleteProject, self).setUp()
        self.req_d = project_models.ProjectCreateRequest('vping')
        fake_pymongo.tokens.insert({"access_token": "12345"})
        self.basePath = '/api/v1/projects'
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()

    @executor.delete(httplib.FORBIDDEN, message.invalid_token())
    def test_projectDeleteTokenIvalid(self):
        self.headers['X-Auth-Token'] = '1234'
        return self.req_d.name

    @executor.delete(httplib.UNAUTHORIZED, message.unauthorized())
    def test_projectDeleteTokenUnauthorized(self):
        self.headers.pop('X-Auth-Token')
        return self.req_d.name

    @executor.delete(httplib.OK, '_delete_success')
    def test_projectDeleteTokenSuccess(self):
        return self.req_d.name

    def _delete_success(self, body):
        self.assertEqual('', body)


class TestTokenUpdateProject(TestToken):
    def setUp(self):
        super(TestTokenUpdateProject, self).setUp()
        self.req_d = project_models.ProjectCreateRequest('vping')
        fake_pymongo.tokens.insert({"access_token": "12345"})
        self.basePath = '/api/v1/projects'
        self.headers['X-Auth-Token'] = '12345'
        self.create_d()

    @executor.update(httplib.FORBIDDEN, message.invalid_token())
    def test_projectUpdateTokenIvalid(self):
        self.headers['X-Auth-Token'] = '1234'
        req = project_models.ProjectUpdateRequest('newName', 'new description')
        return req, self.req_d.name

    @executor.update(httplib.UNAUTHORIZED, message.unauthorized())
    def test_projectUpdateTokenUnauthorized(self):
        self.headers.pop('X-Auth-Token')
        req = project_models.ProjectUpdateRequest('newName', 'new description')
        return req, self.req_d.name

    @executor.update(httplib.OK, '_update_success')
    def test_projectUpdateTokenSuccess(self):
        req = project_models.ProjectUpdateRequest('newName', 'new description')
        return req, self.req_d.name

    def _update_success(self, request, body):
        self.assertIn(request.name, body)


if __name__ == '__main__':
    unittest.main()
