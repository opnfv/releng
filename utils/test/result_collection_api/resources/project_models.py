__author__ = '__serena__'


class ProjectCreateRequest(object):
    def __init__(self, name='', description=''):
        self.name = name
        self.description = description

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
        }


class Project:
    """ Describes a test project"""

    def __init__(self):
        self._id = None
        self.name = None
        self.description = None
        self.creation_date = None

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


class Projects(object):
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
