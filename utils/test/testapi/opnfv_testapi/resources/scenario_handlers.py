import opnfv_testapi.resources.scenario_models as models
from opnfv_testapi.resources import handlers
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
