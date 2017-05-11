from opnfv_testapi.resources import models
from opnfv_testapi.tornado_swagger import swagger


def list_default(value):
    return value if value else list()


def dict_default(value):
    return value if value else dict()


@swagger.model()
class ScenarioTI(models.ModelBase):
    def __init__(self, date=None, status='silver'):
        self.date = date
        self.status = status


@swagger.model()
class ScenarioScore(models.ModelBase):
    def __init__(self, date=None, score='0'):
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
                 project='',
                 customs=None,
                 scores=None,
                 trust_indicators=None):
        self.project = project
        self.customs = list_default(customs)
        self.scores = list_default(scores)
        self.trust_indicators = list_default(trust_indicators)

    @staticmethod
    def attr_parser():
        return {'scores': ScenarioScore,
                'trust_indicators': ScenarioTI}

    def __eq__(self, other):
        return [self.project == other.project and
                self._customs_eq(other) and
                self._scores_eq(other) and
                self._ti_eq(other)]

    def __ne__(self, other):
        return not self.__eq__(other)

    def _customs_eq(self, other):
        return set(self.customs) == set(other.customs)

    def _scores_eq(self, other):
        return set(self.scores) == set(other.scores)

    def _ti_eq(self, other):
        return set(self.trust_indicators) == set(other.trust_indicators)


@swagger.model()
class ScenarioVersion(models.ModelBase):
    """
        @property projects:
        @ptype projects: C{list} of L{ScenarioProject}
    """
    def __init__(self, version=None, projects=None):
        self.version = version
        self.projects = list_default(projects)

    @staticmethod
    def attr_parser():
        return {'projects': ScenarioProject}

    def __eq__(self, other):
        return [self.version == other.version and self._projects_eq(other)]

    def __ne__(self, other):
        return not self.__eq__(other)

    def _projects_eq(self, other):
        for s_project in self.projects:
            for o_project in other.projects:
                if s_project.project == o_project.project:
                    if s_project != o_project:
                        return False

        return True


@swagger.model()
class ScenarioInstaller(models.ModelBase):
    """
        @property versions:
        @ptype versions: C{list} of L{ScenarioVersion}
    """
    def __init__(self, installer=None, versions=None):
        self.installer = installer
        self.versions = list_default(versions)

    @staticmethod
    def attr_parser():
        return {'versions': ScenarioVersion}

    def __eq__(self, other):
        return [self.installer == other.installer and self._versions_eq(other)]

    def __ne__(self, other):
        return not self.__eq__(other)

    def _versions_eq(self, other):
        for s_version in self.versions:
            for o_version in other.versions:
                if s_version.version == o_version.version:
                    if s_version != o_version:
                        return False

        return True


@swagger.model()
class ScenarioCreateRequest(models.ModelBase):
    """
        @property installers:
        @ptype installers: C{list} of L{ScenarioInstaller}
    """
    def __init__(self, name='', installers=None):
        self.name = name
        self.installers = list_default(installers)

    @staticmethod
    def attr_parser():
        return {'installers': ScenarioInstaller}


@swagger.model()
class ScenarioUpdateRequest(models.ModelBase):
    """
        @property field: update field
        @property op: add/delete/update
        @property locate: information used to locate the field
        @property term: new value
    """
    def __init__(self, field=None, op=None, locate=None, term=None):
        self.field = field
        self.op = op
        self.locate = dict_default(locate)
        self.term = dict_default(term)


@swagger.model()
class Scenario(models.ModelBase):
    """
        @property installers:
        @ptype installers: C{list} of L{ScenarioInstaller}
    """
    def __init__(self, name='', create_date='', _id='', installers=None):
        self.name = name
        self._id = _id
        self.creation_date = create_date
        self.installers = list_default(installers)

    @staticmethod
    def attr_parser():
        return {'installers': ScenarioInstaller}

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return [self.name == other.name and self._installers_eq(other)]

    def _installers_eq(self, other):
        for s_install in self.installers:
            for o_install in other.installers:
                if s_install.installer == o_install.installer:
                    if s_install != o_install:
                        return False

        return True


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
