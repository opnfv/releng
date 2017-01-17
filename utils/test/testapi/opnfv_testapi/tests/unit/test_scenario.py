import json
import os

from opnfv_testapi.common.constants import HTTP_BAD_REQUEST
from opnfv_testapi.common.constants import HTTP_FORBIDDEN
from opnfv_testapi.common.constants import HTTP_OK
from opnfv_testapi.resources.scenario_models import ScenarioCreateRequest
from test_testcase import TestBase


class TestScenarioBase(TestBase):
    def setUp(self):
        super(TestScenarioBase, self).setUp()
        self.basePath = '/api/v1/scenarios'
        self.load_request('scenario-create.json')

    def tearDown(self):
        pass

    def assert_body(self, project, req=None):
        pass

    def load_request(self, f_req):
        with open(os.path.join(os.path.dirname(__file__), f_req), 'r') as f:
            self.req_d = json.dumps(json.load(f))
            f.close()


class TestScenarioCreate(TestScenarioBase):
    def test_withoutBody(self):
        (code, body) = self.create()
        self.assertEqual(code, HTTP_BAD_REQUEST)

    def test_emptyName(self):
        req_empty = ScenarioCreateRequest('')
        (code, body) = self.create(req_empty)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('name missing', body)

    def test_noneName(self):
        req_none = ScenarioCreateRequest(None)
        (code, body) = self.create(req_none)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('name missing', body)

    def test_success(self):
        (code, body) = self.create_d()
        self.assertEqual(code, HTTP_OK)
        self.assert_create_body(body)

    def test_alreadyExist(self):
        self.create_d()
        (code, body) = self.create_d()
        self.assertEqual(code, HTTP_FORBIDDEN)
        self.assertIn('already exists', body)
