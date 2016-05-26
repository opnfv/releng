import unittest

from test_base import TestBase
from resources.pod_models import PodCreateRequest, Pod, Pods
from common.constants import HTTP_OK, HTTP_BAD_REQUEST, \
    HTTP_FORBIDDEN, HTTP_NOT_FOUND


class TestPodBase(TestBase):
    def setUp(self):
        super(TestPodBase, self).setUp()
        self.req_d = PodCreateRequest('zte-1', 'virtual',
                                      'zte pod 1', 'ci-pod')
        self.req_e = PodCreateRequest('zte-2', 'metal', 'zte pod 2')
        self.get_res = Pod
        self.list_res = Pods
        self.basePath = '/pods'

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
        self.assertEqual(code, HTTP_BAD_REQUEST)

    def test_success(self):
        code, body = self.create_d()
        self.assertEqual(code, HTTP_OK)
        self.assert_create_body(body)

    def test_alreadyExist(self):
        self.create_d()
        code, body = self.create_d()
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn('already exists', body)

    def _assertMeta(self, meta, success):
        self.assertEqual(meta.success, success)
        if success:
            self.assertEqual(meta.uri, '/pods/{}'.format(self.req_d.name))


class TestPodGet(TestPodBase):
    def test_notExist(self):
        code, body = self.get('notExist')
        self.assertEqual(code, HTTP_NOT_FOUND)

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
