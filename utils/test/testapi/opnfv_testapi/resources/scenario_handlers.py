import functools

from opnfv_testapi.common import message
from opnfv_testapi.common import raises
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

    @swagger.operation(nickname="updateScenarioByName")
    def put(self, name):
        """
            @description: update a single scenario by name
            @param body: fields to be updated
            @type body: L{ScenarioUpdateRequest}
            @in body: body
            @rtype: L{Scenario}
            @return 200: update success
            @raise 404: scenario not exist
            @raise 403: nothing to update
        """
        query = {'name': name}
        db_keys = ['name']
        self._update(query=query, db_keys=db_keys)

    @swagger.operation(nickname="deleteScenarioByName")
    def delete(self, name):
        """
        @description: delete a scenario by name
        @return 200: delete success
        @raise 404: scenario not exist:
        """

        self._delete(query={'name': name})

    def _update_query(self, keys, data):
        query = dict()
        if self._is_rename():
            new = self._term.get('name')
            if data.get('name') != new:
                query['name'] = new

        return query

    def _update_requests(self, data):
        updates = {
            ('name', 'update'): self._update_requests_rename,
            ('installer', 'add'): self._update_requests_add_installer,
            ('installer', 'delete'): self._update_requests_delete_installer,
            ('version', 'add'): self._update_requests_add_version,
            ('version', 'delete'): self._update_requests_delete_version,
            ('owner', 'update'): self._update_requests_change_owner,
            ('project', 'add'): self._update_requests_add_project,
            ('project', 'delete'): self._update_requests_delete_project,
            ('customs', 'add'): self._update_requests_add_customs,
            ('customs', 'delete'): self._update_requests_delete_customs,
            ('score', 'add'): self._update_requests_add_score,
            ('trust_indicator', 'add'): self._update_requests_add_ti,
        }

        updates[(self._field, self._op)](data)

        return data.format()

    def _iter_installers(xstep):
        @functools.wraps(xstep)
        def magic(self, data):
            [xstep(self, installer)
             for installer in self._filter_installers(data.installers)]
        return magic

    def _iter_versions(xstep):
        @functools.wraps(xstep)
        def magic(self, installer):
            [xstep(self, version)
             for version in (self._filter_versions(installer.versions))]
        return magic

    def _iter_projects(xstep):
        @functools.wraps(xstep)
        def magic(self, version):
            [xstep(self, project)
             for project in (self._filter_projects(version.projects))]
        return magic

    def _update_requests_rename(self, data):
        data.name = self._term.get('name')
        if not data.name:
            raises.BadRequest(message.missing('name'))

    def _update_requests_add_installer(self, data):
        data.installers.append(models.ScenarioInstaller.from_dict(self._term))

    def _update_requests_delete_installer(self, data):
        data.installers = self._remove_installers(data.installers)

    @_iter_installers
    def _update_requests_add_version(self, installer):
        installer.versions.append(models.ScenarioVersion.from_dict(self._term))

    @_iter_installers
    def _update_requests_delete_version(self, installer):
        installer.versions = self._remove_versions(installer.versions)

    @_iter_installers
    @_iter_versions
    def _update_requests_change_owner(self, version):
        version.owner = self._term.get('owner')

    @_iter_installers
    @_iter_versions
    def _update_requests_add_project(self, version):
        version.projects.append(models.ScenarioProject.from_dict(self._term))

    @_iter_installers
    @_iter_versions
    def _update_requests_delete_project(self, version):
        version.projects = self._remove_projects(version.projects)

    @_iter_installers
    @_iter_versions
    @_iter_projects
    def _update_requests_add_customs(self, project):
        project.customs = list(set(project.customs + self._term))

    @_iter_installers
    @_iter_versions
    @_iter_projects
    def _update_requests_delete_customs(self, project):
        project.customs = filter(
            lambda f: f not in self._term,
            project.customs)

    @_iter_installers
    @_iter_versions
    @_iter_projects
    def _update_requests_add_score(self, project):
        project.scores.append(
            models.ScenarioScore.from_dict(self._term))

    @_iter_installers
    @_iter_versions
    @_iter_projects
    def _update_requests_add_ti(self, project):
        project.trust_indicators.append(
            models.ScenarioTI.from_dict(self._term))

    def _is_rename(self):
        return self._field == 'name' and self._op == 'update'

    def _remove_installers(self, installers):
        return self._remove('installer', installers)

    def _filter_installers(self, installers):
        return self._filter('installer', installers)

    def _remove_versions(self, versions):
        return self._remove('version', versions)

    def _filter_versions(self, versions):
        return self._filter('version', versions)

    def _remove_projects(self, projects):
        return self._remove('project', projects)

    def _filter_projects(self, projects):
        return self._filter('project', projects)

    def _remove(self, field, fields):
        return filter(
            lambda f: getattr(f, field) != self._locate.get(field),
            fields)

    def _filter(self, field, fields):
        return filter(
            lambda f: getattr(f, field) == self._locate.get(field),
            fields)

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
