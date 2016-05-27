from tornado_swagger_ui.tornado_swagger import swagger

__author__ = '__serena__'


@swagger.model()
class ProjectCreateRequest(object):
    def __init__(self, name, description=''):
        self.name = name
        self.description = description

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
        }


@swagger.model()
class ProjectUpdateRequest(object):
    def __init__(self, name='', description=''):
        self.name = name
        self.description = description

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
        }


@swagger.model()
class Project(object):
    def __init__(self,
                 name=None, _id=None, description=None, create_date=None):
        self._id = _id
        self.name = name
        self.description = description
        self.creation_date = create_date

    @staticmethod
    def from_dict(res_dict):

        if res_dict is None:
            return None

        t = Project()
        t._id = res_dict.get('_id')
        t.creation_date = res_dict.get('creation_date')
        t.name = res_dict.get('name')
        t.description = res_dict.get('description')

        return t

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "creation_date": str(self.creation_date)
        }

    def format_http(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "description": self.description,
            "creation_date": str(self.creation_date),
        }


@swagger.model()
class Projects(object):
    """
        @ptype projects: C{list} of L{Project}
    """
    def __init__(self, projects=list()):
        self.projects = projects

    @staticmethod
    def from_dict(res_dict):
        if res_dict is None:
            return None

        res = Projects()
        for project in res_dict.get('projects'):
            res.projects.append(Project.from_dict(project))
        return res
