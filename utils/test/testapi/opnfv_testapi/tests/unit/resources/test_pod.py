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
from opnfv_testapi.tests.unit import fake_pymongo
from opnfv_testapi.tests.unit.resources import test_base as base


class TestPodBase(base.TestBase):
    def setUp(self):
        super(TestPodBase, self).setUp()
        self.get_res = pod_models.Pod
        self.list_res = pod_models.Pods
        self.basePath = '/api/v1/pods'
        self.req_d = pod_models.PodCreateRequest(name=self.pod_d.name,
                                                 mode=self.pod_d.mode,
                                                 details=self.pod_d.details,
                                                 role=self.pod_d.role)
        self.req_e = pod_models.PodCreateRequest(name=self.pod_e.name,
                                                 mode=self.pod_e.mode,
                                                 details=self.pod_e.details,
                                                 role=self.pod_e.role)

    def assert_get_body(self, pod, req=None):
        if not req:
            req = self.req_d
        self.assertEqual(pod.owner, 'ValidUser')
        self.assertEqual(pod.name, req.name)
        self.assertEqual(pod.mode, req.mode)
        self.assertEqual(pod.details, req.details)
        self.assertEqual(pod.role, req.role)
        self.assertIsNotNone(pod.creation_date)
        self.assertIsNotNone(pod._id)


class TestPodCreate(TestPodBase):
    @executor.create(httplib.BAD_REQUEST, message.not_login())
    def test_notlogin(self):
        return self.req_d

    @executor.mock_invalid_lfid()
    @executor.create(httplib.BAD_REQUEST, message.not_lfid())
    def test_invalidLfid(self):
        return self.req_d

    @executor.mock_valid_lfid()
    @executor.create(httplib.BAD_REQUEST, message.no_body())
    def test_withoutBody(self):
        return None

    @executor.mock_valid_lfid()
    @executor.create(httplib.BAD_REQUEST, message.missing('name'))
    def test_emptyName(self):
        return pod_models.PodCreateRequest('')

    @executor.mock_valid_lfid()
    @executor.create(httplib.BAD_REQUEST, message.missing('name'))
    def test_noneName(self):
        return pod_models.PodCreateRequest(None)

    @executor.mock_valid_lfid()
    @executor.create(httplib.OK, 'assert_create_body')
    def test_success(self):
        return self.req_d

    @executor.mock_valid_lfid()
    @executor.create(httplib.FORBIDDEN, message.exist_base)
    def test_alreadyExist(self):
        fake_pymongo.pods.insert(self.pod_d.format())
        return self.req_d

    @executor.mock_valid_lfid()
    @executor.create(httplib.FORBIDDEN, message.exist_base)
    def test_alreadyExistCaseInsensitive(self):
        fake_pymongo.pods.insert(self.pod_d.format())
        self.req_d.name = self.req_d.name.upper()
        return self.req_d


class TestPodGet(TestPodBase):
    def setUp(self):
        super(TestPodGet, self).setUp()
        fake_pymongo.pods.insert(self.pod_d.format())
        fake_pymongo.pods.insert(self.pod_e.format())

    @executor.get(httplib.NOT_FOUND, message.not_found_base)
    def test_notExist(self):
        return 'notExist'

    @executor.get(httplib.OK, 'assert_get_body')
    def test_getOne(self):
        return self.pod_d.name

    @executor.get(httplib.OK, '_assert_list')
    def test_list(self):
        return None

    def _assert_list(self, body):
        self.assertEqual(len(body.pods), 2)
        for pod in body.pods:
            if self.pod_d.name == pod.name:
                self.assert_get_body(pod)
            else:
                self.assert_get_body(pod, self.pod_e)


if __name__ == '__main__':
    unittest.main()
