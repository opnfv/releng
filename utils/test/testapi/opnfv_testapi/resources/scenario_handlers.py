import functools

from opnfv_testapi.resources import handlers
import opnfv_testapi.resources.scenario_models as models
from opnfv_testapi.tornado_swagger import swagger


class GenericScenarioHandler(handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericScenarioHandler, self).__init__(application,
                                                     request,
                                                     **kwargs)
        self.table = self.db_scenarios
        self.table_cls = models.Scenario

    def set_query(self, filters):
        query = dict()
        elem_query = dict()
        for k, v in filters.iteritems():
            if k == 'scenario':
                query['name'] = v
            elif k == 'installer':
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

        self._list(query=_set_query())

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
        def query():
            return {'name': self.json_args.get('name')}
        miss_fields = ['name']
        self._create(miss_fields=miss_fields, query=query)


class ScenarioGURHandler(GenericScenarioHandler):
    @swagger.operation(nickname='getScenarioByName')
    def get(self, name):
        """
            @description: get a single scenario by name
            @rtype: L{Scenario}
            @return 200: scenario exist
            @raise 404: scenario not exist
        """
        self._get_one(query={'name': name})
        pass

    def put(self, name):
        pass

    @swagger.operation(nickname="deleteScenarioByName")
    def delete(self, name):
        """
        @description: delete a scenario by name
        @return 200: delete success
        @raise 404: scenario not exist:
        """
        self._delete(query={'name': name})


class ScenarioUpdater(object):
    def __init__(self, data, body=None,
                 installer=None, version=None, project=None):
        self.data = data
        self.body = body
        self.installer = installer
        self.version = version
        self.project = project

    def update(self, item, op):
        updates = {
            ('score', 'add'): self._update_requests_add_score,
        }
        updates[(item, op)](self.data)

        return self.data.format()

    def iter_installers(xstep):
        @functools.wraps(xstep)
        def magic(self, data):
            [xstep(self, installer)
             for installer in self._filter_installers(data.installers)]
        return magic

    def iter_versions(xstep):
        @functools.wraps(xstep)
        def magic(self, installer):
            [xstep(self, version)
             for version in (self._filter_versions(installer.versions))]
        return magic

    def iter_projects(xstep):
        @functools.wraps(xstep)
        def magic(self, version):
            [xstep(self, project)
             for project in (self._filter_projects(version.projects))]
        return magic

    @iter_installers
    @iter_versions
    @iter_projects
    def _update_requests_add_score(self, project):
        project.scores.append(
            models.ScenarioScore.from_dict(self.body))

    def _filter_installers(self, installers):
        return self._filter('installer', installers)

    def _filter_versions(self, versions):
        return self._filter('version', versions)

    def _filter_projects(self, projects):
        return self._filter('project', projects)

    def _filter(self, item, items):
        return filter(
            lambda f: getattr(f, item) == getattr(self, item),
            items)


class ScenarioScoresHandler(GenericScenarioHandler):
    @swagger.operation(nickname="addScoreRecord")
    def post(self, scenario):
        """
        @description: add a new score record
        @notes: add a new score record to a project
            POST /api/v1/scenarios/<scenario_name>/scores? \
                installer=<installer_name>& \
                version=<version_name>& \
                project=<project_name>
        @param body: score to be added
        @type body: L{ScenarioScore}
        @in body: body
        @param installer: installer type
        @type installer: L{string}
        @in installer: query
        @required installer: True
        @param version: version
        @type version: L{string}
        @in version: query
        @required version: True
        @param project: project name
        @type project: L{string}
        @in project: query
        @required project: True
        @rtype: L{Scenario}
        @return 200: score is created.
        @raise 404:  scenario/installer/version/project not existed
        """
        self.installer = self.get_query_argument('installer')
        self.version = self.get_query_argument('version')
        self.project = self.get_query_argument('project')

        filters = {'scenario': scenario,
                   'installer': self.installer,
                   'version': self.version,
                   'project': self.project}
        db_keys = ['name']
        self._update(query=self.set_query(filters=filters), db_keys=db_keys)

    def _update_requests(self, data):
        return ScenarioUpdater(data,
                               self.json_args,
                               self.installer,
                               self.version,
                               self.project).update('score', 'add')
