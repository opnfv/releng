##############################################################################
# Copyright (c) 2016 ZTE Corporation
# feng.xiaowei@zte.com.cn
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
import httplib
import unittest

from opnfv_testapi.common import message
from opnfv_testapi.resources import pod_models
import test_base as base


class TestPodBase(base.TestBase):
    def setUp(self):
        super(TestPodBase, self).setUp()
        self.req_d = pod_models.PodCreateRequest('zte-1', 'virtual',
                                                 'zte pod 1', 'ci-pod')
        self.req_e = pod_models.PodCreateRequest('zte-2', 'metal', 'zte pod 2')
        self.get_res = pod_models.Pod
        self.list_res = pod_models.Pods
        self.basePath = '/api/v1/pods'

    def assert_get_body(self, pod, req=None):
        if not req:
            req = self.req_d
        self.assertEqual(pod.name, req.name)
        self.assertEqual(pod.mode, req.mode)
        self.assertEqual(pod.details, req.details)
        self.assertEqual(pod.role, req.role)
        self.assertIsNotNone(pod.creation_date)
        self.assertIsNotNone(pod._id)


class TestPodCreate(TestPodBase):
    def test_withoutBody(self):
        (code, body) = self.create()
        self.assertEqual(code, httplib.BAD_REQUEST)

    def test_emptyName(self):
        req_empty = pod_models.PodCreateRequest('')
        (code, body) = self.create(req_empty)
        self.assertEqual(code, httplib.BAD_REQUEST)
        self.assertIn(message.missing('name'), body)

    def test_noneName(self):
        req_none = pod_models.PodCreateRequest(None)
        (code, body) = self.create(req_none)
        self.assertEqual(code, httplib.BAD_REQUEST)
        self.assertIn(message.missing('name'), body)

    def test_success(self):
        code, body = self.create_d()
        self.assertEqual(code, httplib.OK)
        self.assert_create_body(body)

    def test_alreadyExist(self):
        self.create_d()
        code, body = self.create_d()
        self.assertEqual(code, httplib.FORBIDDEN)
        self.assertIn(message.exist_base, body)


class TestPodGet(TestPodBase):
    def test_notExist(self):
        code, body = self.get('notExist')
        self.assertEqual(code, httplib.NOT_FOUND)

    def test_getOne(self):
        self.create_d()
        code, body = self.get(self.req_d.name)
        self.assert_get_body(body)

    def test_list(self):
        self.create_d()
        self.create_e()
        code, body = self.get()
        self.assertEqual(len(body.pods), 2)
        for pod in body.pods:
            if self.req_d.name == pod.name:
                self.assert_get_body(pod)
            else:
                self.assert_get_body(pod, self.req_e)

if __name__ == '__main__':
    unittest.main()
