import functools

from opnfv_testapi.common import message
from opnfv_testapi.common import raises
from opnfv_testapi.handlers import base_handlers
import opnfv_testapi.models.scenario_models as models
from opnfv_testapi.tornado_swagger import swagger


class GenericScenarioHandler(base_handlers.GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericScenarioHandler, self).__init__(application,
                                                     request,
                                                     **kwargs)
        self.table = self.db_scenarios
        self.table_cls = models.Scenario

    def set_query(self, locators):
        query = dict()
        elem_query = dict()
        for k, v in locators.iteritems():
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

    @swagger.operation(nickname="updateScenarioName")
    def put(self, name):
        """
            @description: update scenario, only rename is supported currently
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


class ScenarioUpdater(object):
    def __init__(self, data, body=None,
                 installer=None, version=None, project=None):
        self.data = data
        self.body = body
        self.installer = installer
        self.version = version
        self.project = project

    def update(self, item, action):
        updates = {
            ('scores', 'post'): self._update_requests_add_score,
            ('trust_indicators', 'post'): self._update_requests_add_ti,
            ('customs', 'post'): self._update_requests_add_customs,
            ('customs', 'put'): self._update_requests_update_customs,
            ('customs', 'delete'): self._update_requests_delete_customs,
            ('projects', 'post'): self._update_requests_add_projects,
            ('projects', 'put'): self._update_requests_update_projects,
            ('projects', 'delete'): self._update_requests_delete_projects,
            ('owner', 'put'): self._update_requests_change_owner,
            ('versions', 'post'): self._update_requests_add_versions,
            ('versions', 'put'): self._update_requests_update_versions,
            ('versions', 'delete'): self._update_requests_delete_versions,
            ('installers', 'post'): self._update_requests_add_installers,
            ('installers', 'put'): self._update_requests_update_installers,
            ('installers', 'delete'): self._update_requests_delete_installers,
        }
        updates[(item, action)](self.data)

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

    @iter_installers
    @iter_versions
    @iter_projects
    def _update_requests_add_ti(self, project):
        project.trust_indicators.append(
            models.ScenarioTI.from_dict(self.body))

    @iter_installers
    @iter_versions
    @iter_projects
    def _update_requests_add_customs(self, project):
        project.customs = list(set(project.customs + self.body))

    @iter_installers
    @iter_versions
    @iter_projects
    def _update_requests_update_customs(self, project):
        project.customs = list(set(self.body))

    @iter_installers
    @iter_versions
    @iter_projects
    def _update_requests_delete_customs(self, project):
        project.customs = filter(
            lambda f: f not in self.body,
            project.customs)

    @iter_installers
    @iter_versions
    def _update_requests_add_projects(self, version):
        version.projects = self._update_with_body(models.ScenarioProject,
                                                  'project',
                                                  version.projects)

    @iter_installers
    @iter_versions
    def _update_requests_update_projects(self, version):
        version.projects = self._update_with_body(models.ScenarioProject,
                                                  'project',
                                                  list())

    @iter_installers
    @iter_versions
    def _update_requests_delete_projects(self, version):
        version.projects = self._remove_projects(version.projects)

    @iter_installers
    @iter_versions
    def _update_requests_change_owner(self, version):
        version.owner = self.body.get('owner')

    @iter_installers
    def _update_requests_add_versions(self, installer):
        installer.versions = self._update_with_body(models.ScenarioVersion,
                                                    'version',
                                                    installer.versions)

    @iter_installers
    def _update_requests_update_versions(self, installer):
        installer.versions = self._update_with_body(models.ScenarioVersion,
                                                    'version',
                                                    list())

    @iter_installers
    def _update_requests_delete_versions(self, installer):
        installer.versions = self._remove_versions(installer.versions)

    def _update_requests_add_installers(self, scenario):
        scenario.installers = self._update_with_body(models.ScenarioInstaller,
                                                     'installer',
                                                     scenario.installers)

    def _update_requests_update_installers(self, scenario):
        scenario.installers = self._update_with_body(models.ScenarioInstaller,
                                                     'installer',
                                                     list())

    def _update_requests_delete_installers(self, scenario):
        scenario.installers = self._remove_installers(scenario.installers)

    def _update_with_body(self, clazz, field, withs):
        exists = list()
        malformat = list()
        for new in self.body:
            try:
                format_new = clazz.from_dict_with_raise(new)
                new_name = getattr(format_new, field)
                if not any(getattr(o, field) == new_name for o in withs):
                    withs.append(format_new)
                else:
                    exists.append(new_name)
            except Exception as error:
                malformat.append(error.message)
        if malformat:
            raises.BadRequest(message.bad_format(malformat))
        elif exists:
            raises.Conflict(message.exist('{}s'.format(field), exists))
        return withs

    def _filter_installers(self, installers):
        return self._filter('installer', installers)

    def _remove_installers(self, installers):
        return self._remove('installer', installers)

    def _filter_versions(self, versions):
        return self._filter('version', versions)

    def _remove_versions(self, versions):
        return self._remove('version', versions)

    def _filter_projects(self, projects):
        return self._filter('project', projects)

    def _remove_projects(self, projects):
        return self._remove('project', projects)

    def _filter(self, item, items):
        return filter(
            lambda f: getattr(f, item) == getattr(self, item),
            items)

    def _remove(self, field, fields):
        return filter(
            lambda f: getattr(f, field) not in self.body,
            fields)


class GenericScenarioUpdateHandler(GenericScenarioHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericScenarioUpdateHandler, self).__init__(application,
                                                           request,
                                                           **kwargs)
        self.installer = None
        self.version = None
        self.project = None
        self.item = None
        self.action = None

    def do_update(self, item, action, locators):
        self.item = item
        self.action = action
        for k, v in locators.iteritems():
            if not v:
                v = self.get_query_argument(k)
                setattr(self, k, v)
                locators[k] = v
        self.pure_update(query=self.set_query(locators=locators))

    def _update_requests(self, data):
        return ScenarioUpdater(data,
                               self.json_args,
                               self.installer,
                               self.version,
                               self.project).update(self.item, self.action)


class ScenarioScoresHandler(GenericScenarioUpdateHandler):
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
        @return 200: score is created.
        @raise 404:  scenario/installer/version/project not existed
        """
        self.do_update('scores',
                       'post',
                       locators={'scenario': scenario,
                                 'installer': None,
                                 'version': None,
                                 'project': None})


class ScenarioTIsHandler(GenericScenarioUpdateHandler):
    @swagger.operation(nickname="addTrustIndicatorRecord")
    def post(self, scenario):
        """
        @description: add a new trust indicator record
        @notes: add a new trust indicator record to a project
            POST /api/v1/scenarios/<scenario_name>/trust_indicators? \
                installer=<installer_name>& \
                version=<version_name>& \
                project=<project_name>
        @param body: trust indicator to be added
        @type body: L{ScenarioTI}
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
        @return 200: trust indicator is added.
        @raise 404:  scenario/installer/version/project not existed
        """
        self.do_update('trust_indicators',
                       'post',
                       locators={'scenario': scenario,
                                 'installer': None,
                                 'version': None,
                                 'project': None})


class ScenarioCustomsHandler(GenericScenarioUpdateHandler):
    @swagger.operation(nickname="addCustomizedTestCases")
    def post(self, scenario):
        """
        @description: add customized test cases
        @notes: add several test cases to a project
            POST /api/v1/scenarios/<scenario_name>/customs? \
                installer=<installer_name>& \
                version=<version_name>& \
                project=<project_name>
        @param body: test cases to be added
        @type body: C{list} of L{string}
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
        @return 200: test cases are added.
        @raise 404:  scenario/installer/version/project not existed
        """
        self.do_update('customs',
                       'post',
                       locators={'scenario': scenario,
                                 'installer': None,
                                 'version': None,
                                 'project': None})

    @swagger.operation(nickname="updateCustomizedTestCases")
    def put(self, scenario):
        """
        @description: update customized test cases
        @notes: substitute all the customized test cases
            PUT /api/v1/scenarios/<scenario_name>/customs? \
                installer=<installer_name>& \
                version=<version_name>& \
                project=<project_name>
        @param body: new supported test cases
        @type body: C{list} of L{string}
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
        @return 200: substitute test cases success.
        @raise 404:  scenario/installer/version/project not existed
        """
        self.do_update('customs',
                       'put',
                       locators={'scenario': scenario,
                                 'installer': None,
                                 'version': None,
                                 'project': None})

    @swagger.operation(nickname="deleteCustomizedTestCases")
    def delete(self, scenario):
        """
        @description: delete one or several customized test cases
        @notes: delete one or some customized test cases
            DELETE /api/v1/scenarios/<scenario_name>/customs? \
                installer=<installer_name>& \
                version=<version_name>& \
                project=<project_name>
        @param body: test case(s) to be deleted
        @type body: C{list} of L{string}
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
        @return 200: delete test case(s) success.
        @raise 404:  scenario/installer/version/project not existed
        """
        self.do_update('customs',
                       'delete',
                       locators={'scenario': scenario,
                                 'installer': None,
                                 'version': None,
                                 'project': None})


class ScenarioProjectsHandler(GenericScenarioUpdateHandler):
    @swagger.operation(nickname="addProjectsUnderScenario")
    def post(self, scenario):
        """
        @description: add projects to scenario
        @notes: add one or multiple projects
            POST /api/v1/scenarios/<scenario_name>/projects? \
                installer=<installer_name>& \
                version=<version_name>
        @param body: projects to be added
        @type body: C{list} of L{ScenarioProject}
        @in body: body
        @param installer: installer type
        @type installer: L{string}
        @in installer: query
        @required installer: True
        @param version: version
        @type version: L{string}
        @in version: query
        @required version: True
        @return 200: projects are added.
        @raise 400: bad schema
        @raise 409: conflict, project already exists
        @raise 404:  scenario/installer/version not existed
        """
        self.do_update('projects',
                       'post',
                       locators={'scenario': scenario,
                                 'installer': None,
                                 'version': None})

    @swagger.operation(nickname="updateScenarioProjects")
    def put(self, scenario):
        """
        @description: replace all projects
        @notes: substitute all projects, delete existed ones with new provides
            PUT /api/v1/scenarios/<scenario_name>/projects? \
                installer=<installer_name>& \
                version=<version_name>
        @param body: new projects
        @type body: C{list} of L{ScenarioProject}
        @in body: body
        @param installer: installer type
        @type installer: L{string}
        @in installer: query
        @required installer: True
        @param version: version
        @type version: L{string}
        @in version: query
        @required version: True
        @return 200: replace projects success.
        @raise 400: bad schema
        @raise 404:  scenario/installer/version not existed
        """
        self.do_update('projects',
                       'put',
                       locators={'scenario': scenario,
                                 'installer': None,
                                 'version': None})

    @swagger.operation(nickname="deleteProjectsUnderScenario")
    def delete(self, scenario):
        """
        @description: delete one or multiple projects
        @notes: delete one or multiple projects
            DELETE /api/v1/scenarios/<scenario_name>/projects? \
                installer=<installer_name>& \
                version=<version_name>
        @param body: projects(names) to be deleted
        @type body: C{list} of L{string}
        @in body: body
        @param installer: installer type
        @type installer: L{string}
        @in installer: query
        @required installer: True
        @param version: version
        @type version: L{string}
        @in version: query
        @required version: True
        @return 200: delete project(s) success.
        @raise 404:  scenario/installer/version not existed
        """
        self.do_update('projects',
                       'delete',
                       locators={'scenario': scenario,
                                 'installer': None,
                                 'version': None})


class ScenarioOwnerHandler(GenericScenarioUpdateHandler):
    @swagger.operation(nickname="changeScenarioOwner")
    def put(self, scenario):
        """
        @description: change scenario owner
        @notes: substitute all projects, delete existed ones with new provides
            PUT /api/v1/scenarios/<scenario_name>/owner? \
                installer=<installer_name>& \
                version=<version_name>
        @param body: new owner
        @type body: L{ScenarioChangeOwnerRequest}
        @in body: body
        @param installer: installer type
        @type installer: L{string}
        @in installer: query
        @required installer: True
        @param version: version
        @type version: L{string}
        @in version: query
        @required version: True
        @return 200: change owner success.
        @raise 404:  scenario/installer/version not existed
        """
        self.do_update('owner',
                       'put',
                       locators={'scenario': scenario,
                                 'installer': None,
                                 'version': None})


class ScenarioVersionsHandler(GenericScenarioUpdateHandler):
    @swagger.operation(nickname="addVersionsUnderScenario")
    def post(self, scenario):
        """
        @description: add versions to scenario
        @notes: add one or multiple versions
            POST /api/v1/scenarios/<scenario_name>/versions? \
                installer=<installer_name>
        @param body: versions to be added
        @type body: C{list} of L{ScenarioVersion}
        @in body: body
        @param installer: installer type
        @type installer: L{string}
        @in installer: query
        @required installer: True
        @return 200: versions are added.
        @raise 400: bad schema
        @raise 409: conflict, version already exists
        @raise 404:  scenario/installer not exist
        """
        self.do_update('versions',
                       'post',
                       locators={'scenario': scenario,
                                 'installer': None})

    @swagger.operation(nickname="updateVersionsUnderScenario")
    def put(self, scenario):
        """
        @description: replace all versions
        @notes: substitute all versions as a totality
            PUT /api/v1/scenarios/<scenario_name>/versions? \
                installer=<installer_name>
        @param body: new versions
        @type body: C{list} of L{ScenarioVersion}
        @in body: body
        @param installer: installer type
        @type installer: L{string}
        @in installer: query
        @required installer: True
        @return 200: replace versions success.
        @raise 400: bad schema
        @raise 404:  scenario/installer not exist
        """
        self.do_update('versions',
                       'put',
                       locators={'scenario': scenario,
                                 'installer': None})

    @swagger.operation(nickname="deleteVersionsUnderScenario")
    def delete(self, scenario):
        """
        @description: delete one or multiple versions
        @notes: delete one or multiple versions
            DELETE /api/v1/scenarios/<scenario_name>/versions? \
                installer=<installer_name>
        @param body: versions(names) to be deleted
        @type body: C{list} of L{string}
        @in body: body
        @param installer: installer type
        @type installer: L{string}
        @in installer: query
        @required installer: True
        @return 200: delete versions success.
        @raise 404:  scenario/installer not exist
        """
        self.do_update('versions',
                       'delete',
                       locators={'scenario': scenario,
                                 'installer': None})


class ScenarioInstallersHandler(GenericScenarioUpdateHandler):
    @swagger.operation(nickname="addInstallersUnderScenario")
    def post(self, scenario):
        """
        @description: add installers to scenario
        @notes: add one or multiple installers
            POST /api/v1/scenarios/<scenario_name>/installers
        @param body: installers to be added
        @type body: C{list} of L{ScenarioInstaller}
        @in body: body
        @return 200: installers are added.
        @raise 400: bad schema
        @raise 409: conflict, installer already exists
        @raise 404:  scenario not exist
        """
        self.do_update('installers',
                       'post',
                       locators={'scenario': scenario})

    @swagger.operation(nickname="updateInstallersUnderScenario")
    def put(self, scenario):
        """
        @description: replace all installers
        @notes: substitute all installers as a totality
            PUT /api/v1/scenarios/<scenario_name>/installers
        @param body: new installers
        @type body: C{list} of L{ScenarioInstaller}
        @in body: body
        @return 200: replace versions success.
        @raise 400: bad schema
        @raise 404:  scenario/installer not exist
        """
        self.do_update('installers',
                       'put',
                       locators={'scenario': scenario})

    @swagger.operation(nickname="deleteInstallersUnderScenario")
    def delete(self, scenario):
        """
        @description: delete one or multiple installers
        @notes: delete one or multiple installers
            DELETE /api/v1/scenarios/<scenario_name>/installers
        @param body: installers(names) to be deleted
        @type body: C{list} of L{string}
        @in body: body
        @return 200: delete versions success.
        @raise 404:  scenario/installer not exist
        """
        self.do_update('installers',
                       'delete',
                       locators={'scenario': scenario})
