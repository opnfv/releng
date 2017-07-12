import functools
import httplib
import json
import os
from copy import deepcopy
from datetime import datetime

import opnfv_testapi.resources.scenario_models as models
from opnfv_testapi.common import message
from opnfv_testapi.tests.unit.resources import test_base as base


class TestScenarioBase(base.TestBase):
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
        self.assertEqual(code, httplib.OK)
        if req is None:
            req = self.req_d
        self.assertIsNotNone(scenario._id)
        self.assertIsNotNone(scenario.creation_date)

        scenario == models.Scenario.from_dict(req)

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
        self.assertEqual(code, httplib.BAD_REQUEST)

    def test_emptyName(self):
        req_empty = models.ScenarioCreateRequest('')
        (code, body) = self.create(req_empty)
        self.assertEqual(code, httplib.BAD_REQUEST)
        self.assertIn(message.missing('name'), body)

    def test_noneName(self):
        req_none = models.ScenarioCreateRequest(None)
        (code, body) = self.create(req_none)
        self.assertEqual(code, httplib.BAD_REQUEST)
        self.assertIn(message.missing('name'), body)

    def test_success(self):
        (code, body) = self.create_d()
        self.assertEqual(code, httplib.OK)
        self.assert_create_body(body)

    def test_alreadyExist(self):
        self.create_d()
        (code, body) = self.create_d()
        self.assertEqual(code, httplib.FORBIDDEN)
        self.assertIn(message.exist_base, body)


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
            self.assertEqual(code, httplib.OK)
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
        self.scenario_2 = self.create_return_name(self.req_2)

    def _execute(set_update):
        @functools.wraps(set_update)
        def magic(self):
            update, scenario = set_update(self, deepcopy(self.req_d))
            self._update_and_assert(update, scenario)
        return magic

    def _update(expected):
        def _update(set_update):
            @functools.wraps(set_update)
            def wrap(self):
                update, scenario = set_update(self, deepcopy(self.req_d))
                code, body = self.update(update, self.scenario)
                getattr(self, expected)(code, scenario)
            return wrap
        return _update

    @_update('_success')
    def test_renameScenario(self, scenario):
        new_name = 'nosdn-nofeature-noha'
        scenario['name'] = new_name
        update_req = models.ScenarioUpdateRequest(field='name',
                                                  op='update',
                                                  locate={},
                                                  term={'name': new_name})
        return update_req, scenario

    @_update('_forbidden')
    def test_renameScenario_exist(self, scenario):
        new_name = self.scenario_2
        scenario['name'] = new_name
        update_req = models.ScenarioUpdateRequest(field='name',
                                                  op='update',
                                                  locate={},
                                                  term={'name': new_name})
        return update_req, scenario

    @_update('_bad_request')
    def test_renameScenario_noName(self, scenario):
        new_name = self.scenario_2
        scenario['name'] = new_name
        update_req = models.ScenarioUpdateRequest(field='name',
                                                  op='update',
                                                  locate={},
                                                  term={})
        return update_req, scenario

    @_execute
    def test_addInstaller(self, scenario):
        add = models.ScenarioInstaller(installer='daisy', versions=list())
        scenario['installers'].append(add.format())
        update = models.ScenarioUpdateRequest(field='installer',
                                              op='add',
                                              locate={},
                                              term=add.format())
        return update, scenario

    @_execute
    def test_deleteInstaller(self, scenario):
        scenario['installers'] = filter(lambda f: f['installer'] != 'apex',
                                        scenario['installers'])

        update = models.ScenarioUpdateRequest(field='installer',
                                              op='delete',
                                              locate={'installer': 'apex'})
        return update, scenario

    @_execute
    def test_addVersion(self, scenario):
        add = models.ScenarioVersion(version='danube', projects=list())
        scenario['installers'][0]['versions'].append(add.format())
        update = models.ScenarioUpdateRequest(field='version',
                                              op='add',
                                              locate={'installer': 'apex'},
                                              term=add.format())
        return update, scenario

    @_execute
    def test_deleteVersion(self, scenario):
        scenario['installers'][0]['versions'] = filter(
            lambda f: f['version'] != 'master',
            scenario['installers'][0]['versions'])

        update = models.ScenarioUpdateRequest(field='version',
                                              op='delete',
                                              locate={'installer': 'apex',
                                                      'version': 'master'})
        return update, scenario

    @_execute
    def test_changeOwner(self, scenario):
        scenario['installers'][0]['versions'][0]['owner'] = 'lucy'

        update = models.ScenarioUpdateRequest(field='owner',
                                              op='update',
                                              locate={'installer': 'apex',
                                                      'version': 'master'},
                                              term={'owner': 'lucy'})
        return update, scenario

    @_execute
    def test_addProject(self, scenario):
        add = models.ScenarioProject(project='qtip').format()
        scenario['installers'][0]['versions'][0]['projects'].append(add)
        update = models.ScenarioUpdateRequest(field='project',
                                              op='add',
                                              locate={'installer': 'apex',
                                                      'version': 'master'},
                                              term=add)
        return update, scenario

    @_execute
    def test_deleteProject(self, scenario):
        scenario['installers'][0]['versions'][0]['projects'] = filter(
            lambda f: f['project'] != 'functest',
            scenario['installers'][0]['versions'][0]['projects'])

        update = models.ScenarioUpdateRequest(field='project',
                                              op='delete',
                                              locate={
                                                  'installer': 'apex',
                                                  'version': 'master',
                                                  'project': 'functest'})
        return update, scenario

    @_execute
    def test_addCustoms(self, scenario):
        add = ['odl', 'parser', 'vping_ssh']
        projects = scenario['installers'][0]['versions'][0]['projects']
        functest = filter(lambda f: f['project'] == 'functest', projects)[0]
        functest['customs'] = ['healthcheck', 'odl', 'parser', 'vping_ssh']
        update = models.ScenarioUpdateRequest(field='customs',
                                              op='add',
                                              locate={
                                                  'installer': 'apex',
                                                  'version': 'master',
                                                  'project': 'functest'},
                                              term=add)
        return update, scenario

    @_execute
    def test_deleteCustoms(self, scenario):
        projects = scenario['installers'][0]['versions'][0]['projects']
        functest = filter(lambda f: f['project'] == 'functest', projects)[0]
        functest['customs'] = ['healthcheck']
        update = models.ScenarioUpdateRequest(field='customs',
                                              op='delete',
                                              locate={
                                                  'installer': 'apex',
                                                  'version': 'master',
                                                  'project': 'functest'},
                                              term=['vping_ssh'])
        return update, scenario

    @_execute
    def test_addScore(self, scenario):
        add = models.ScenarioScore(date=str(datetime.now()), score='11/12')
        projects = scenario['installers'][0]['versions'][0]['projects']
        functest = filter(lambda f: f['project'] == 'functest', projects)[0]
        functest['scores'].append(add.format())
        update = models.ScenarioUpdateRequest(field='score',
                                              op='add',
                                              locate={
                                                  'installer': 'apex',
                                                  'version': 'master',
                                                  'project': 'functest'},
                                              term=add.format())
        return update, scenario

    @_execute
    def test_addTi(self, scenario):
        add = models.ScenarioTI(date=str(datetime.now()), status='gold')
        projects = scenario['installers'][0]['versions'][0]['projects']
        functest = filter(lambda f: f['project'] == 'functest', projects)[0]
        functest['trust_indicators'].append(add.format())
        update = models.ScenarioUpdateRequest(field='trust_indicator',
                                              op='add',
                                              locate={
                                                  'installer': 'apex',
                                                  'version': 'master',
                                                  'project': 'functest'},
                                              term=add.format())
        return update, scenario

    def _update_and_assert(self, update_req, new_scenario, name=None):
        code, _ = self.update(update_req, self.scenario)
        self.assertEqual(code, httplib.OK)
        self._get_and_assert(_none_default(name, self.scenario),
                             new_scenario)

    def _success(self, status, new_scenario):
        self.assertEqual(status, httplib.OK)
        self._get_and_assert(new_scenario.get('name'), new_scenario)

    def _forbidden(self, status, new_scenario):
        self.assertEqual(status, httplib.FORBIDDEN)

    def _bad_request(self, status, new_scenario):
        self.assertEqual(status, httplib.BAD_REQUEST)


class TestScenarioDelete(TestScenarioBase):
    def test_notFound(self):
        code, body = self.delete('notFound')
        self.assertEqual(code, httplib.NOT_FOUND)

    def test_success(self):
        scenario = self.create_return_name(self.req_d)
        code, _ = self.delete(scenario)
        self.assertEqual(code, httplib.OK)
        code, _ = self.get(scenario)
        self.assertEqual(code, httplib.NOT_FOUND)


def _none_default(check, default):
    return check if check else default
