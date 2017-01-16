from opnfv_testapi.common.constants import HTTP_FORBIDDEN
from opnfv_testapi.resources.handlers import GenericApiHandler
from opnfv_testapi.resources.scenario_models import Scenario
from opnfv_testapi.tornado_swagger import swagger


class GenericScenarioHandler(GenericApiHandler):
    def __init__(self, application, request, **kwargs):
        super(GenericScenarioHandler, self).__init__(application,
                                                     request,
                                                     **kwargs)
        self.table = self.db_scenarios
        self.table_cls = Scenario


class ScenariosCLHandler(GenericScenarioHandler):
    @swagger.operation(nickname="List scenarios by queries")
    def get(self):
        """
            @description: Retrieve scenario(s).
            @notes: Retrieve scenario(s)
            @return 200: all scenarios consist with query,
                         empty list if no scenario is found
            @rtype: L{Scenarios}
        """
        self._list()

    @swagger.operation(nickname="Create a new scenario")
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
    @swagger.operation(nickname='Get the scenario by name')
    def get(self, name):
        """
            @description: get a single scenario by name
            @rtype: L{Scenario}
            @return 200: scenario exist
            @raise 404: scenario not exist
        """
        pass

    @swagger.operation(nickname="Update the scenario by name")
    def put(self, name):
        """
            @description: update a single scenario by name
            @param body: fields to be updated
            @type body: L{string}
            @in body: body
            @rtype: L{Scenario}
            @return 200: update success
            @raise 404: scenario not exist
            @raise 403: nothing to update
        """
        pass
