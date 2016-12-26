import models
from opnfv_testapi.tornado_swagger import swagger


@swagger.model()
class ScenarioTI(models.ModelBase):
    def __init__(self, date=None, status='silver'):
        self.date = date
        self.status = status


@swagger.model()
class ScenarioScore(models.ModelBase):
    def __init__(self, date=None, score=''):
        self.date = date
        self.score = score


@swagger.model()
class ScenarioProject(models.ModelBase):
    """
        @property customs:
        @ptype customs: C{list} of L{string}
        @property scores:
        @ptype scores: C{list} of L{ScenarioScore}
        @property trust_indicators:
        @ptype trust_indicators: C{list} of L{ScenarioTI}
    """
    def __init__(self,
                 name='',
                 customs=None,
                 scores=None,
                 trust_indicators=None):
        self.name = name
        self.customs = customs
        self.scores = scores
        self.trust_indicator = trust_indicators


@swagger.model()
class ScenarioInstaller(models.ModelBase):
    """
        @property projects:
        @ptype projects: C{list} of L{ScenarioProject}
    """
    def __init__(self, installer, owner='', projects=None):
        self.installer = installer
        self.owner = owner
        self.projects = projects


@swagger.model()
class Scenario(models.ModelBase):
    """
        @property installers:
        @ptype installers: C{list} of L{ScenarioInstaller}
    """
    def __init__(self, name='', create_date='', _id='', installers=None):
        self.name = name
        self._id = _id
        self.create_date = create_date
        self.installers = installers


@swagger.model()
class Scenarios(models.ModelBase):
    """
        @property scenarios:
        @ptype scenarios: C{list} of L{Scenario}
    """
    def __init__(self):
        self.scenarios = list()

    @staticmethod
    def attr_parser():
        return {'scenarios': Scenario}
