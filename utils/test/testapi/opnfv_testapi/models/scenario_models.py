from opnfv_testapi.models import base_models
from opnfv_testapi.tornado_swagger import swagger


def list_default(value):
    return value if value else list()


def dict_default(value):
    return value if value else dict()


@swagger.model()
class ScenarioTI(base_models.ModelBase):
    def __init__(self, date=None, status='silver'):
        self.date = date
        self.status = status

    def __eq__(self, other):
        return (self.date == other.date and
                self.status == other.status)

    def __ne__(self, other):
        return not self.__eq__(other)


@swagger.model()
class ScenarioScore(base_models.ModelBase):
    def __init__(self, date=None, score='0'):
        self.date = date
        self.score = score

    def __eq__(self, other):
        return (self.date == other.date and
                self.score == other.score)

    def __ne__(self, other):
        return not self.__eq__(other)


@swagger.model()
class ScenarioProject(base_models.ModelBase):
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
        return (self.project == other.project and
                self._customs_eq(other) and
                self._scores_eq(other) and
                self._ti_eq(other))

    def __ne__(self, other):
        return not self.__eq__(other)

    def _customs_eq(self, other):
        return set(self.customs) == set(other.customs)

    def _scores_eq(self, other):
        return self.scores == other.scores

    def _ti_eq(self, other):
        return self.trust_indicators == other.trust_indicators


@swagger.model()
class ScenarioVersion(base_models.ModelBase):
    """
        @property projects:
        @ptype projects: C{list} of L{ScenarioProject}
    """
    def __init__(self, owner=None, version=None, projects=None):
        self.owner = owner
        self.version = version
        self.projects = list_default(projects)

    @staticmethod
    def attr_parser():
        return {'projects': ScenarioProject}

    def __eq__(self, other):
        return (self.version == other.version and
                self.owner == other.owner and
                self._projects_eq(other))

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
class ScenarioInstaller(base_models.ModelBase):
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
        return (self.installer == other.installer and self._versions_eq(other))

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
class ScenarioCreateRequest(base_models.ModelBase):
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
class ScenarioChangeOwnerRequest(base_models.ModelBase):
    def __init__(self, owner=None):
        self.owner = owner


@swagger.model()
class ScenarioUpdateRequest(base_models.ModelBase):
    def __init__(self, name=None):
        self.name = name


@swagger.model()
class Scenario(base_models.ModelBase):
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
        return (self.name == other.name and self._installers_eq(other))

    def _installers_eq(self, other):
        for s_install in self.installers:
            for o_install in other.installers:
                if s_install.installer == o_install.installer:
                    if s_install != o_install:
                        return False

        return True


@swagger.model()
class Scenarios(base_models.ModelBase):
    """
        @property scenarios:
        @ptype scenarios: C{list} of L{Scenario}
    """
    def __init__(self):
        self.scenarios = list()

    @staticmethod
    def attr_parser():
        return {'scenarios': Scenario}
