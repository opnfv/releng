##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from datetime import datetime
import json
from os import path

from bson.objectid import ObjectId
import mock
from tornado import testing

from opnfv_testapi.models import base_models
from opnfv_testapi.models import pod_models
from opnfv_testapi.tests.unit import fake_pymongo


class TestBase(testing.AsyncHTTPTestCase):
    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    def setUp(self):
        self._patch_server()
        self.basePath = ''
        self.create_res = base_models.CreateResponse
        self.get_res = None
        self.list_res = None
        self.update_res = None
        self.pod_d = pod_models.Pod(name='zte-pod1',
                                    mode='virtual',
                                    details='zte pod 1',
                                    role='community-ci',
                                    _id=str(ObjectId()),
                                    owner='ValidUser',
                                    create_date=str(datetime.now()))
        self.pod_e = pod_models.Pod(name='zte-pod2',
                                    mode='metal',
                                    details='zte pod 2',
                                    role='production-ci',
                                    _id=str(ObjectId()),
                                    owner='ValidUser',
                                    create_date=str(datetime.now()))
        self.req_d = None
        self.req_e = None
        self.addCleanup(self._clear)
        super(TestBase, self).setUp()
        fake_pymongo.users.insert({"user": "ValidUser",
                                   'email': 'validuser@lf.com',
                                   'fullname': 'Valid User',
                                   'groups': [
                                       'opnfv-testapi-users',
                                       'opnfv-gerrit-functest-submitters',
                                       'opnfv-gerrit-qtip-contributors']
                                   })

    def tearDown(self):
        self.db_patcher.stop()
        self.config_patcher.stop()

    def _patch_server(self):
        import argparse
        config = path.join(path.dirname(__file__),
                           '../../../../etc/config.ini')
        self.config_patcher = mock.patch(
            'argparse.ArgumentParser.parse_known_args',
            return_value=(argparse.Namespace(config_file=config), None))
        self.db_patcher = mock.patch('opnfv_testapi.db.api.DB',
                                     fake_pymongo)
        self.config_patcher.start()
        self.db_patcher.start()

    def get_app(self):
        from opnfv_testapi.cmd import server
        return server.make_app()

    def create_d(self, *args):
        return self.create(self.req_d, *args)

    def create_e(self, *args):
        return self.create(self.req_e, *args)

    def create(self, req=None, *args):
        return self.create_help(self.basePath, req, *args)

    def create_help(self, uri, req, *args):
        return self.post_direct_url(self._update_uri(uri, *args), req)

    def post_direct_url(self, url, req):
        if req and not isinstance(req, str) and hasattr(req, 'format'):
            req = req.format()
        res = self.fetch(url,
                         method='POST',
                         body=json.dumps(req),
                         headers=self.headers)

        return self._get_return(res, self.create_res)

    def get(self, *args):
        res = self.fetch(self._get_uri(*args),
                         method='GET',
                         headers=self.headers)

        def inner():
            new_args, num = self._get_valid_args(*args)
            return self.get_res \
                if num != self._need_arg_num(self.basePath) else self.list_res
        return self._get_return(res, inner())

    def query(self, query):
        res = self.fetch(self._get_query_uri(query),
                         method='GET',
                         headers=self.headers)
        return self._get_return(res, self.list_res)

    def update_direct_url(self, url, new=None):
        if new and hasattr(new, 'format'):
            new = new.format()
        res = self.fetch(url,
                         method='PUT',
                         body=json.dumps(new),
                         headers=self.headers)
        return self._get_return(res, self.update_res)

    def update(self, new=None, *args):
        return self.update_direct_url(self._get_uri(*args), new)

    def delete_direct_url(self, url, body):
        if body:
            res = self.fetch(url,
                             method='DELETE',
                             body=json.dumps(body),
                             headers=self.headers,
                             allow_nonstandard_methods=True)
        else:
            res = self.fetch(url,
                             method='DELETE',
                             headers=self.headers)

        return res.code, res.body

    def delete(self, *args):
        return self.delete_direct_url(self._get_uri(*args), None)

    @staticmethod
    def _get_valid_args(*args):
        new_args = tuple(['%s' % arg for arg in args if arg is not None])
        return new_args, len(new_args)

    def _need_arg_num(self, uri):
        return uri.count('%s')

    def _get_query_uri(self, query):
        return self.basePath + '?' + query if query else self.basePath

    def _get_uri(self, *args):
        return self._update_uri(self.basePath, *args)

    def _update_uri(self, uri, *args):
        r_uri = uri
        new_args, num = self._get_valid_args(*args)
        if num != self._need_arg_num(uri):
            r_uri += '/%s'

        return r_uri % tuple(['%s' % arg for arg in new_args])

    def _get_return(self, res, cls):
        code = res.code
        body = res.body
        if body:
            return code, self._get_return_body(code, body, cls)
        else:
            return code, None

    @staticmethod
    def _get_return_body(code, body, cls):
        return cls.from_dict(json.loads(body)) if code < 300 and cls else body

    def assert_href(self, body):
        self.assertIn(self.basePath, body.href)

    def assert_create_body(self, body, req=None, *args):
        import inspect
        if not req:
            req = self.req_d
        resource_name = ''
        if inspect.isclass(req):
            resource_name = req.name
        elif isinstance(req, dict):
            resource_name = req['name']
        elif isinstance(req, str):
            resource_name = json.loads(req)['name']
        new_args = args + tuple([resource_name])
        self.assertIn(self._get_uri(*new_args), body.href)

    @staticmethod
    def _clear():
        fake_pymongo.pods.clear()
        fake_pymongo.projects.clear()
        fake_pymongo.testcases.clear()
        fake_pymongo.results.clear()
        fake_pymongo.scenarios.clear()
