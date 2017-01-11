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
            @type body: L{string}
            @rtype: L{CreateResponse}
        """
        pass


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
