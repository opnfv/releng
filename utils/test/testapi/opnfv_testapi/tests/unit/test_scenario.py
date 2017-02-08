from copy import deepcopy
import json
import os

from opnfv_testapi.common.constants import HTTP_BAD_REQUEST
from opnfv_testapi.common.constants import HTTP_FORBIDDEN
from opnfv_testapi.common.constants import HTTP_OK
import opnfv_testapi.resources.scenario_models as models
from test_testcase import TestBase


class TestScenarioBase(TestBase):
    def setUp(self):
        super(TestScenarioBase, self).setUp()
        self.get_res = models.Scenario
        self.list_res = models.Scenarios
        self.basePath = '/api/v1/scenarios'
        self.req_d = self._load_request('scenario-c1.json')
        self.req_2 = self._load_request('scenario-c2.json')

    def tearDown(self):
        pass

    def assert_body(self, project, req=None):
        pass

    @staticmethod
    def _load_request(f_req):
        abs_file = os.path.join(os.path.dirname(__file__), f_req)
        with open(abs_file, 'r') as f:
            loader = json.load(f)
            f.close()
        return loader

    def create_return_name(self, req):
        _, res = self.create(req)
        return res.href.split('/')[-1]

    def assert_res(self, code, scenario, req=None):
        self.assertEqual(code, HTTP_OK)
        if req is None:
            req = self.req_d
        scenario_dict = scenario.format_http()
        self.assertIsNotNone(scenario_dict['_id'])
        self.assertIsNotNone(scenario_dict['creation_date'])
        self.assertDictContainsSubset(req, scenario_dict)

    @staticmethod
    def _set_query(*args):
        uri = ''
        for arg in args:
            uri += arg + '&'
        return uri[0: -1]

    def _get_and_assert(self, name, req=None):
        code, body = self.get(name)
        self.assert_res(code, body, req)


class TestScenarioCreate(TestScenarioBase):
    def test_withoutBody(self):
        (code, body) = self.create()
        self.assertEqual(code, HTTP_BAD_REQUEST)

    def test_emptyName(self):
        req_empty = models.ScenarioCreateRequest('')
        (code, body) = self.create(req_empty)
        self.assertEqual(code, HTTP_BAD_REQUEST)
        self.assertIn('name missing', body)

    def test_noneName(self):
        req_none = models.ScenarioCreateRequest(None)
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


class TestScenarioGet(TestScenarioBase):
    def setUp(self):
        super(TestScenarioGet, self).setUp()
        self.scenario_1 = self.create_return_name(self.req_d)
        self.scenario_2 = self.create_return_name(self.req_2)

    def test_getByName(self):
        self._get_and_assert(self.scenario_1, self.req_d)

    def test_getAll(self):
        self._query_and_assert(query=None, reqs=[self.req_d, self.req_2])

    def test_queryName(self):
        query = self._set_query('name=nosdn-nofeature-ha')
        self._query_and_assert(query, reqs=[self.req_d])

    def test_queryInstaller(self):
        query = self._set_query('installer=apex')
        self._query_and_assert(query, reqs=[self.req_d])

    def test_queryVersion(self):
        query = self._set_query('version=master')
        self._query_and_assert(query, reqs=[self.req_d])

    def test_queryProject(self):
        query = self._set_query('project=functest')
        self._query_and_assert(query, reqs=[self.req_d, self.req_2])

    def test_queryCombination(self):
        query = self._set_query('name=nosdn-nofeature-ha',
                                'installer=apex',
                                'version=master',
                                'project=functest')

        self._query_and_assert(query, reqs=[self.req_d])

    def _query_and_assert(self, query, found=True, reqs=None):
        code, body = self.query(query)
        if not found:
            self.assertEqual(code, HTTP_OK)
            self.assertEqual(0, len(body.scenarios))
        else:
            self.assertEqual(len(reqs), len(body.scenarios))
            for req in reqs:
                for scenario in body.scenarios:
                    if req['name'] == scenario.name:
                        self.assert_res(code, scenario, req)


class TestScenarioUpdate(TestScenarioBase):
    def setUp(self):
        super(TestScenarioUpdate, self).setUp()
        self.scenario = self.create_return_name(self.req_d)

    def test_renameScenario(self):
        new_name = 'nosdn-nofeature-noha'
        new_scenario = deepcopy(self.req_d)
        new_scenario['name'] = new_name
        update_req = models.ScenarioUpdateRequest(field='name',
                                                  op='update',
                                                  locate={},
                                                  term={'name': new_name})
        self._update_and_assert(update_req, new_scenario, new_name)

    def test_addInstaller(self):
        add = models.ScenarioInstaller(installer='daisy', versions=list())
        new_scenario = deepcopy(self.req_d)
        new_scenario['installers'].append(add.format())
        update_req = models.ScenarioUpdateRequest(field='installer',
                                                  op='add',
                                                  locate={},
                                                  term=add)
        self._update_and_assert(update_req, new_scenario)

    def test_deleteInstaller(self):
        new_scenario = deepcopy(self.req_d)
        new_scenario['installers'] = filter(lambda f: f['installer'] != 'apex',
                                            new_scenario['installers'])

        update_req = models.ScenarioUpdateRequest(field='installer',
                                                  op='delete',
                                                  locate={'installer': 'apex'})
        self._update_and_assert(update_req, new_scenario)

    def test_addVersion(self):
        add = models.ScenarioVersion(version='danube', projects=list())
        new_scenario = deepcopy(self.req_d)
        new_scenario['installers'][0]['versions'].append(add.format())
        update_req = models.ScenarioUpdateRequest(field='version',
                                                  op='add',
                                                  locate={'installer': 'apex'},
                                                  term=add)
        self._update_and_assert(update_req, new_scenario)

    def test_deleteVersion(self):
        new_scenario = deepcopy(self.req_d)
        new_scenario['installers'][0]['versions'] = filter(
            lambda f: f['version'] != 'master',
            new_scenario['installers'][0]['versions'])

        update_req = models.ScenarioUpdateRequest(field='version',
                                                  op='delete',
                                                  locate={'installer': 'apex',
                                                          'version': 'master'})
        self._update_and_assert(update_req, new_scenario)

    def _update_and_assert(self, update_req, new_scenario, name=None):
        code, _ = self.update(update_req, self.scenario)
        self.assertEqual(code, HTTP_OK)
        self._get_and_assert(self._none_default(name, self.scenario),
                             new_scenario)

    @staticmethod
    def _none_default(check, default):
        return check if check else default
