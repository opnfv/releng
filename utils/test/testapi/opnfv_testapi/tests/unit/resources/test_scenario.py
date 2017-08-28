import functools
import httplib
import json
import os

from datetime import datetime

from opnfv_testapi.common import message
import opnfv_testapi.resources.scenario_models as models
from opnfv_testapi.tests.unit.resources import test_base as base


def _none_default(check, default):
    return check if check else default


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
        self.assertEqual(scenario, models.Scenario.from_dict(req))

    @staticmethod
    def set_query(*args):
        uri = ''
        for arg in args:
            uri += arg + '&'
        return uri[0: -1]

    def get_and_assert(self, name):
        code, body = self.get(name)
        self.assert_res(code, body, self.req_d)


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
        self.get_and_assert(self.scenario_1)

    def test_getAll(self):
        self._query_and_assert(query=None, reqs=[self.req_d, self.req_2])

    def test_queryName(self):
        query = self.set_query('name=nosdn-nofeature-ha')
        self._query_and_assert(query, reqs=[self.req_d])

    def test_queryInstaller(self):
        query = self.set_query('installer=apex')
        self._query_and_assert(query, reqs=[self.req_d])

    def test_queryVersion(self):
        query = self.set_query('version=master')
        self._query_and_assert(query, reqs=[self.req_d])

    def test_queryProject(self):
        query = self.set_query('project=functest')
        self._query_and_assert(query, reqs=[self.req_d, self.req_2])

    # close due to random fail, open again after solve it in another patch
    # def test_queryCombination(self):
    #     query = self._set_query('name=nosdn-nofeature-ha',
    #                             'installer=apex',
    #                             'version=master',
    #                             'project=functest')
    #
    #     self._query_and_assert(query, reqs=[self.req_d])

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


class TestScenarioUpdate(TestScenarioBase):
    def setUp(self):
        super(TestScenarioUpdate, self).setUp()
        self.scenario = self.create_return_name(self.req_d)
        self.scenario_2 = self.create_return_name(self.req_2)
        self.update_url = ''
        self.scenario_url = '/api/v1/scenarios/{}'.format(self.scenario)
        self.installer = self.req_d['installers'][0]['installer']
        self.version = self.req_d['installers'][0]['versions'][0]['version']
        self.locate_project = 'installer={}&version={}&project={}'.format(
            self.installer,
            self.version,
            'functest')

    def update_url_fixture(item):
        def _update_url_fixture(xstep):
            def wrapper(self, *args, **kwargs):
                self.update_url = '{}/{}'.format(self.scenario_url, item)
                locator = None
                if item in ['projects', 'owner']:
                    locator = 'installer={}&version={}'.format(
                        self.installer,
                        self.version)
                elif item in ['versions']:
                    locator = 'installer={}'.format(
                        self.installer)
                elif item in ['rename']:
                    self.update_url = self.scenario_url

                if locator:
                    self.update_url = '{}?{}'.format(self.update_url, locator)

                xstep(self, *args, **kwargs)
            return wrapper
        return _update_url_fixture

    def update_partial(operate, expected):
        def _update_partial(set_update):
            @functools.wraps(set_update)
            def wrapper(self):
                update = set_update(self)
                code, body = getattr(self, operate)(update)
                getattr(self, expected)(code)
            return wrapper
        return _update_partial

    @update_partial('_add', '_success')
    def test_addScore(self):
        add = models.ScenarioScore(date=str(datetime.now()), score='11/12')
        projects = self.req_d['installers'][0]['versions'][0]['projects']
        functest = filter(lambda f: f['project'] == 'functest', projects)[0]
        functest['scores'].append(add.format())
        self.update_url = '{}/scores?{}'.format(self.scenario_url,
                                                self.locate_project)

        return add

    @update_partial('_add', '_success')
    def test_addTrustIndicator(self):
        add = models.ScenarioTI(date=str(datetime.now()), status='gold')
        projects = self.req_d['installers'][0]['versions'][0]['projects']
        functest = filter(lambda f: f['project'] == 'functest', projects)[0]
        functest['trust_indicators'].append(add.format())
        self.update_url = '{}/trust_indicators?{}'.format(self.scenario_url,
                                                          self.locate_project)

        return add

    @update_partial('_add', '_success')
    def test_addCustoms(self):
        adds = ['odl', 'parser', 'vping_ssh']
        projects = self.req_d['installers'][0]['versions'][0]['projects']
        functest = filter(lambda f: f['project'] == 'functest', projects)[0]
        functest['customs'] = list(set(functest['customs'] + adds))
        self.update_url = '{}/customs?{}'.format(self.scenario_url,
                                                 self.locate_project)
        return adds

    @update_partial('_update', '_success')
    def test_updateCustoms(self):
        updates = ['odl', 'parser', 'vping_ssh']
        projects = self.req_d['installers'][0]['versions'][0]['projects']
        functest = filter(lambda f: f['project'] == 'functest', projects)[0]
        functest['customs'] = updates
        self.update_url = '{}/customs?{}'.format(self.scenario_url,
                                                 self.locate_project)

        return updates

    @update_partial('_delete', '_success')
    def test_deleteCustoms(self):
        deletes = ['vping_ssh']
        projects = self.req_d['installers'][0]['versions'][0]['projects']
        functest = filter(lambda f: f['project'] == 'functest', projects)[0]
        functest['customs'] = ['healthcheck']
        self.update_url = '{}/customs?{}'.format(self.scenario_url,
                                                 self.locate_project)

        return deletes

    @update_url_fixture('projects')
    @update_partial('_add', '_success')
    def test_addProjects_succ(self):
        add = models.ScenarioProject(project='qtip').format()
        self.req_d['installers'][0]['versions'][0]['projects'].append(add)
        return [add]

    @update_url_fixture('projects')
    @update_partial('_add', '_conflict')
    def test_addProjects_already_exist(self):
        add = models.ScenarioProject(project='functest').format()
        return [add]

    @update_url_fixture('projects')
    @update_partial('_add', '_bad_request')
    def test_addProjects_bad_schema(self):
        add = models.ScenarioProject(project='functest').format()
        add['score'] = None
        return [add]

    @update_url_fixture('projects')
    @update_partial('_update', '_success')
    def test_updateProjects_succ(self):
        update = models.ScenarioProject(project='qtip').format()
        self.req_d['installers'][0]['versions'][0]['projects'] = [update]
        return [update]

    @update_url_fixture('projects')
    @update_partial('_update', '_conflict')
    def test_updateProjects_duplicated(self):
        update = models.ScenarioProject(project='qtip').format()
        return [update, update]

    @update_url_fixture('projects')
    @update_partial('_update', '_bad_request')
    def test_updateProjects_bad_schema(self):
        update = models.ScenarioProject(project='functest').format()
        update['score'] = None
        return [update]

    @update_url_fixture('projects')
    @update_partial('_delete', '_success')
    def test_deleteProjects(self):
        deletes = ['functest']
        projects = self.req_d['installers'][0]['versions'][0]['projects']
        self.req_d['installers'][0]['versions'][0]['projects'] = filter(
            lambda f: f['project'] != 'functest',
            projects)
        return deletes

    @update_url_fixture('owner')
    @update_partial('_update', '_success')
    def test_changeOwner(self):
        new_owner = 'new_owner'
        update = models.ScenarioChangeOwnerRequest(new_owner).format()
        self.req_d['installers'][0]['versions'][0]['owner'] = new_owner
        return update

    @update_url_fixture('versions')
    @update_partial('_add', '_success')
    def test_addVersions_succ(self):
        add = models.ScenarioVersion(version='Euphrates').format()
        self.req_d['installers'][0]['versions'].append(add)
        return [add]

    @update_url_fixture('versions')
    @update_partial('_add', '_conflict')
    def test_addVersions_already_exist(self):
        add = models.ScenarioVersion(version='master').format()
        return [add]

    @update_url_fixture('versions')
    @update_partial('_add', '_bad_request')
    def test_addVersions_bad_schema(self):
        add = models.ScenarioVersion(version='euphrates').format()
        add['notexist'] = None
        return [add]

    @update_url_fixture('versions')
    @update_partial('_update', '_success')
    def test_updateVersions_succ(self):
        update = models.ScenarioVersion(version='euphrates').format()
        self.req_d['installers'][0]['versions'] = [update]
        return [update]

    @update_url_fixture('versions')
    @update_partial('_update', '_conflict')
    def test_updateVersions_duplicated(self):
        update = models.ScenarioVersion(version='euphrates').format()
        return [update, update]

    @update_url_fixture('versions')
    @update_partial('_update', '_bad_request')
    def test_updateVersions_bad_schema(self):
        update = models.ScenarioVersion(version='euphrates').format()
        update['not_owner'] = 'Iam'
        return [update]

    @update_url_fixture('versions')
    @update_partial('_delete', '_success')
    def test_deleteVersions(self):
        deletes = ['master']
        versions = self.req_d['installers'][0]['versions']
        self.req_d['installers'][0]['versions'] = filter(
            lambda f: f['version'] != 'master',
            versions)
        return deletes

    @update_url_fixture('installers')
    @update_partial('_add', '_success')
    def test_addInstallers_succ(self):
        add = models.ScenarioInstaller(installer='daisy').format()
        self.req_d['installers'].append(add)
        return [add]

    @update_url_fixture('installers')
    @update_partial('_add', '_conflict')
    def test_addInstallers_already_exist(self):
        add = models.ScenarioInstaller(installer='apex').format()
        return [add]

    @update_url_fixture('installers')
    @update_partial('_add', '_bad_request')
    def test_addInstallers_bad_schema(self):
        add = models.ScenarioInstaller(installer='daisy').format()
        add['not_exist'] = 'not_exist'
        return [add]

    @update_url_fixture('installers')
    @update_partial('_update', '_success')
    def test_updateInstallers_succ(self):
        update = models.ScenarioInstaller(installer='daisy').format()
        self.req_d['installers'] = [update]
        return [update]

    @update_url_fixture('installers')
    @update_partial('_update', '_conflict')
    def test_updateInstallers_duplicated(self):
        update = models.ScenarioInstaller(installer='daisy').format()
        return [update, update]

    @update_url_fixture('installers')
    @update_partial('_update', '_bad_request')
    def test_updateInstallers_bad_schema(self):
        update = models.ScenarioInstaller(installer='daisy').format()
        update['not_exist'] = 'not_exist'
        return [update]

    @update_url_fixture('installers')
    @update_partial('_delete', '_success')
    def test_deleteInstallers(self):
        deletes = ['apex']
        installers = self.req_d['installers']
        self.req_d['installers'] = filter(
            lambda f: f['installer'] != 'apex',
            installers)
        return deletes

    @update_url_fixture('rename')
    @update_partial('_update', '_success')
    def test_renameScenario(self):
        new_name = 'new_scenario_name'
        update = models.ScenarioUpdateRequest(name=new_name)
        self.req_d['name'] = new_name
        return update

    @update_url_fixture('rename')
    @update_partial('_update', '_forbidden')
    def test_renameScenario_exist(self):
        new_name = self.req_d['name']
        update = models.ScenarioUpdateRequest(name=new_name)
        return update

    def _add(self, update_req):
        return self.post_direct_url(self.update_url, update_req)

    def _update(self, update_req):
        return self.update_direct_url(self.update_url, update_req)

    def _delete(self, update_req):
        return self.delete_direct_url(self.update_url, update_req)

    def _success(self, status):
        self.assertEqual(status, httplib.OK)
        self.get_and_assert(self.req_d['name'])

    def _forbidden(self, status):
        self.assertEqual(status, httplib.FORBIDDEN)

    def _bad_request(self, status):
        self.assertEqual(status, httplib.BAD_REQUEST)

    def _conflict(self, status):
        self.assertEqual(status, httplib.CONFLICT)
