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
from opnfv_testapi.tests.unit import executor
from opnfv_testapi.tests.unit.resources import test_base as base


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
    @executor.create(httplib.BAD_REQUEST, message.no_body())
    def test_withoutBody(self):
        return None

    @executor.create(httplib.BAD_REQUEST, message.missing('name'))
    def test_emptyName(self):
        return pod_models.PodCreateRequest('')

    @executor.create(httplib.BAD_REQUEST, message.missing('name'))
    def test_noneName(self):
        return pod_models.PodCreateRequest(None)

    @executor.create(httplib.OK, 'assert_create_body')
    def test_success(self):
        return self.req_d

    @executor.create(httplib.FORBIDDEN, message.exist_base)
    def test_alreadyExist(self):
        self.create_d()
        return self.req_d


class TestPodGet(TestPodBase):
    def setUp(self):
        super(TestPodGet, self).setUp()
        self.create_d()
        self.create_e()

    @executor.get(httplib.NOT_FOUND, message.not_found_base)
    def test_notExist(self):
        return 'notExist'

    @executor.get(httplib.OK, 'assert_get_body')
    def test_getOne(self):
        return self.req_d.name

    @executor.get(httplib.OK, '_assert_list')
    def test_list(self):
        return None

    def _assert_list(self, body):
        self.assertEqual(len(body.pods), 2)
        for pod in body.pods:
            if self.req_d.name == pod.name:
                self.assert_get_body(pod)
            else:
                self.assert_get_body(pod, self.req_e)


if __name__ == '__main__':
    unittest.main()
