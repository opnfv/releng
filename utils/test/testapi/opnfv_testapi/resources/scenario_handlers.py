from opnfv_testapi.common.constants import HTTP_FORBIDDEN
from opnfv_testapi.resources.handlers import GenericApiHandler
from opnfv_testapi.resources.scenario_models import Scenario
import opnfv_testapi.resources.scenario_models as models
from opnfv_testapi.tornado_swagger import swagger


class GenericScenarioHandler(GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericScenarioHandler, self).__init__(application,
                                                     request,
                                                     **kwargs)
        self.table = self.db_scenarios
        self.table_cls = Scenario


class ScenariosCLHandler(GenericScenarioHandler):
    @swagger.operation(nickname="queryScenarios")
    def get(self):
        """
            @description: Retrieve scenario(s).
            @notes: Retrieve scenario(s)
                Available filters for this request are :
                 - name : scenario name

                GET /scenarios?name=scenario_1
            @param name: scenario name
            @type name: L{string}
            @in name: query
            @required name: False
            @param installer: installer type
            @type installer: L{string}
            @in installer: query
            @required installer: False
            @param version: version
            @type version: L{string}
            @in version: query
            @required version: False
            @param project: project name
            @type project: L{string}
            @in project: query
            @required project: False
            @return 200: all scenarios satisfy queries,
                         empty list if no scenario is found
            @rtype: L{Scenarios}
        """

        def _set_query():
            query = dict()
            elem_query = dict()
            for k in self.request.query_arguments.keys():
                v = self.get_query_argument(k)
                if k == 'installer':
                    elem_query["installer"] = v
                elif k == 'version':
                    elem_query["versions.version"] = v
                elif k == 'project':
                    elem_query["versions.projects.project"] = v
                else:
                    query[k] = v
            if elem_query:
                query['installers'] = {'$elemMatch': elem_query}
            return query

        self._list(_set_query())

    @swagger.operation(nickname="createScenario")
    def post(self):
        """
            @description: create a new scenario by name
            @param body: scenario to be created
            @type body: L{ScenarioCreateRequest}
            @in body: body
            @rtype: L{CreateResponse}
            @return 200: scenario is created.
            @raise 403: scenario already exists
            @raise 400:  body or name not provided
        """
        def query(data):
            return {'name': data.name}

        def error(data):
            message = '{} already exists as a scenario'.format(data.name)
            return HTTP_FORBIDDEN, message

        miss_checks = ['name']
        db_checks = [(self.table, False, query, error)]
        self._create(miss_checks=miss_checks, db_checks=db_checks)


class ScenarioGURHandler(GenericScenarioHandler):
    @swagger.operation(nickname='getScenarioByName')
    def get(self, name):
        """
            @description: get a single scenario by name
            @rtype: L{Scenario}
            @return 200: scenario exist
            @raise 404: scenario not exist
        """
        self._get_one({'name': name})
        pass

    @swagger.operation(nickname="updateScenarioByName")
    def put(self, name):
        """
            @description: update a single scenario by name
            @param body: fields to be updated
            @type body: L{ScenarioCreateRequest}
            @in body: body
            @rtype: L{Scenario}
            @return 200: update success
            @raise 404: scenario not exist
            @raise 403: nothing to update
        """
        query = {'name': name}
        db_keys = ['name']
        self._update(query, db_keys)

    def _update_query(self, keys, data):
        query = dict()
        equal = True
        if self._is_rename():
            new = self._term.get('name')
            if data.name != new:
                equal = False
                query['name'] = new

        return equal, query

    def _update_requests(self, data):
        if self._is_rename():
            self._update_requests_rename(data)
        elif self._is_add_installer():
            self._update_requests_add_installer(data)
        elif self._is_delete_installer():
            self._update_requests_delete_installer(data)
        elif self._is_add_version():
            self._update_requests_add_version(data)
        elif self._is_delete_version():
            self._update_requests_delete_version(data)
        elif self._is_change_owner():
            self._update_requests_change_owner(data)
        elif self._is_add_project():
            self._update_requests_add_project(data)
        elif self._is_delete_project():
            self._update_requests_delete_project(data)
        elif self._is_add_customs():
            self._update_requests_add_customs(data)
        elif self._is_delete_customs():
            self._update_requests_delete_customs(data)
        elif self._is_add_score():
            self._update_requests_add_score(data)
        elif self._is_add_ti():
            self._update_requests_add_ti(data)

        return data.format()

    def _update_requests_rename(self, data):
        data.name = self._term.get('name')

    def _update_requests_add_installer(self, data):
        data.installers.append(models.ScenarioInstaller.from_dict(self._term))

    def _update_requests_delete_installer(self, data):
        data.installers = filter(
            lambda f: f.installer != self._locate.get('installer'),
            data.installers)

    def _update_requests_add_version(self, data):
        installers = filter(
            lambda f: f.installer == self._locate.get('installer'),
            data.installers)
        installers[0].versions.append(
            models.ScenarioVersion.from_dict(self._term))

    def _update_requests_delete_version(self, data):
        installers = filter(
            lambda f: f.installer == self._locate.get('installer'),
            data.installers)
        installers[0].versions = filter(
            lambda f: f.version != self._locate.get('version'),
            installers[0].versions)

    def _update_requests_change_owner(self, data):
        installers = filter(
            lambda f: f.installer == self._locate.get('installer'),
            data.installers)
        versions = filter(
            lambda f: f.version == self._locate.get('version'),
            installers[0].versions)
        versions[0].owner = self._term.get('owner')

    def _update_requests_add_project(self, data):
        installers = filter(
            lambda f: f.installer == self._locate.get('installer'),
            data.installers)
        versions = filter(
            lambda f: f.version == self._locate.get('version'),
            installers[0].versions)
        versions[0].projects.append(
            models.ScenarioProject.from_dict(self._term))

    def _update_requests_delete_project(self, data):
        installers = filter(
            lambda f: f.installer == self._locate.get('installer'),
            data.installers)
        versions = filter(
            lambda f: f.version == self._locate.get('version'),
            installers[0].versions)
        versions[0].projects = filter(
            lambda f: f.project != self._locate.get('project'),
            versions[0].projects)

    def _update_requests_add_customs(self, data):
        installers = filter(
            lambda f: f.installer == self._locate.get('installer'),
            data.installers)
        versions = filter(
            lambda f: f.version == self._locate.get('version'),
            installers[0].versions)
        projects = filter(
            lambda f: f.project == self._locate.get('project'),
            versions[0].projects)
        projects[0].customs = list(set(projects[0].customs + self._term))

    def _update_requests_delete_customs(self, data):
        installers = filter(
            lambda f: f.installer == self._locate.get('installer'),
            data.installers)
        versions = filter(
            lambda f: f.version == self._locate.get('version'),
            installers[0].versions)
        projects = filter(
            lambda f: f.project == self._locate.get('project'),
            versions[0].projects)
        projects[0].customs = filter(
            lambda f: f not in self._term,
            projects[0].customs)

    def _update_requests_add_score(self, data):
        installers = filter(
            lambda f: f.installer == self._locate.get('installer'),
            data.installers)
        versions = filter(
            lambda f: f.version == self._locate.get('version'),
            installers[0].versions)
        projects = filter(
            lambda f: f.project == self._locate.get('project'),
            versions[0].projects)
        projects[0].scores.append(models.ScenarioScore.from_dict(self._term))

    def _update_requests_add_ti(self, data):
        installers = filter(
            lambda f: f.installer == self._locate.get('installer'),
            data.installers)
        versions = filter(
            lambda f: f.version == self._locate.get('version'),
            installers[0].versions)
        projects = filter(
            lambda f: f.project == self._locate.get('project'),
            versions[0].projects)
        projects[0].trust_indicators.append(
            models.ScenarioTI.from_dict(self._term))

    def _is_rename(self):
        return self._bool_check(self._is_field('name') and self._is_update())

    def _is_add_installer(self):
        return self._bool_check(self._is_installer() and self._is_add())

    def _is_delete_installer(self):
        return self._bool_check(self._is_installer() and self._is_delete())

    def _is_add_version(self):
        return self._bool_check(self._is_version() and self._is_add())

    def _is_delete_version(self):
        return self._bool_check(self._is_version() and self._is_delete())

    def _is_change_owner(self):
        return self._bool_check(self._is_field('owner') and self._is_update())

    def _is_add_project(self):
        return self._bool_check(self._is_project() and self._is_add())

    def _is_delete_project(self):
        return self._bool_check(self._is_project() and self._is_delete())

    def _is_add_customs(self):
        return self._bool_check(self._is_customs() and self._is_add())

    def _is_delete_customs(self):
        return self._bool_check(self._is_customs() and self._is_delete())

    def _is_add_score(self):
        return self._bool_check(self._is_field('score') and self._is_add())

    def _is_add_ti(self):
        return self._bool_check(
            self._is_field('trust_indicator') and self._is_add())

    def _is_customs(self):
        return self._is_field('customs')

    def _is_project(self):
        return self._is_field('project')

    def _is_version(self):
        return self._is_field('version')

    def _is_installer(self):
        return self._is_field('installer')

    def _is_field(self, item):
        return self._bool_check(self._field == item)

    def _is_update(self):
        return self._bool_check(self._op == 'update')

    def _is_add(self):
        return self._bool_check(self._op == 'add')

    def _is_delete(self):
        return self._bool_check(self._op == 'delete')

    @staticmethod
    def _bool_check(condition):
        return True if condition else False

    @property
    def _field(self):
        return self.json_args.get('field')

    @property
    def _op(self):
        return self.json_args.get('op')

    @property
    def _locate(self):
        return self.json_args.get('locate')

    @property
    def _term(self):
        return self.json_args.get('term')
