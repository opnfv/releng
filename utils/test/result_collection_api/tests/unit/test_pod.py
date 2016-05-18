import unittest
import json

from test_base import TestBase
from resources.pod_models import PodCreateRequest, \
    PodCreateResponse, PodsGetResponse
from common.constants import HTTP_OK, HTTP_BAD_REQUEST, HTTP_FORBIDDEN


class TestPodCreate(TestBase):
    req = PodCreateRequest(name='zte-1', mode='alive', details='zte pod 1')

    def test_withoutBody(self):
        res = self.create('/pods', body=None)
        self.assertEqual(res.code, HTTP_BAD_REQUEST)

    def test_success(self):
        res = self.create('/pods', body=self.req.format())
        self.assertEqual(res.code, HTTP_OK)
        res_body = PodCreateResponse.from_dict(json.loads(res.body))
        self._assertMeta(res_body.meta, True)
        self._assertBody(res_body.pod)

    def test_alreadyExist(self):
        self.create('/pods', body=self.req.format())
        res = self.create('/pods', body=self.req.format())
        self.assertEqual(res.code, HTTP_FORBIDDEN)
        self.assertIn('already exists', res.body)

    def _assertMeta(self, meta, success):
        self.assertEqual(meta.success, success)
        if success:
            self.assertEqual(meta.uri, '/pods/{}'.format(self.req.name))

    def _assertBody(self, res):
        self.assertEqual(res.name, self.req.name)
        self.assertEqual(res.mode, self.req.mode)
        self.assertEqual(res.details, self.req.details)
        self.assertIsNotNone(res.creation_date)
        self.assertIsNotNone(res._id)


class TestPodGet(TestBase):
    def test_notExist(self):
        res = self.get('/pods/notExist')
        body = PodsGetResponse.from_dict(json.loads(res.body))
        self._assertMeta(body.meta, 0)

    def test_getOne(self):
        self.create('/pods', body=TestPodCreate.req.format())
        res = self.get('/pods/{}'.format(TestPodCreate.req.name))
        body = PodsGetResponse.from_dict(json.loads(res.body))
        self._assertMeta(body.meta, 1)
        self._assertBody(TestPodCreate.req, body.pods[0])

    def test_list(self):
        req = PodCreateRequest(name='zte-2', mode='alive', details='zte pod 2')
        self.create('/pods', body=TestPodCreate.req.format())
        self.create('/pods', body=req.format())
        res = self.get('/pods')
        body = PodsGetResponse.from_dict(json.loads(res.body))
        self._assertMeta(body.meta, 2)
        for pod in body.pods:
            if req.name == pod.name:
                self._assertBody(req, pod)
            else:
                self._assertBody(TestPodCreate.req, pod)

    def _assertMeta(self, meta, total):
        def check_success():
            if total is 0:
                return False
            else:
                return True
        self.assertEqual(meta.total, total)
        self.assertEqual(meta.success, check_success())

    def _assertBody(self, req, res):
        self.assertEqual(res.name, req.name)
        self.assertEqual(res.mode, req.mode)
        self.assertEqual(res.details, req.details)
        self.assertIsNotNone(res.creation_date)


if __name__ == '__main__':
    unittest.main()
