class TestcaseCreateRequest(object):
    def __init__(self, url=None, name=None, description=None):
        self.name = name
        self.url = url
        self.description = description

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
        }


class TestcaseUpdateRequest(object):
    def __init__(self, name=None, description=None, project_name=None):
        self.name = name
        self.description = description
        self.project_name = project_name

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "project_name": self.project_name,
        }


class Testcase:
    """ Describes a test case"""

    def __init__(self):
        self._id = None
        self.name = None
        self.project_name = None
        self.description = None
        self.url = None
        self.creation_date = None

    @staticmethod
    def from_dict(a_dict):

        if a_dict is None:
            return None

        t = Testcase()
        t._id = a_dict.get('_id')
        t.project_name = a_dict.get('project_name')
        t.creation_date = a_dict.get('creation_date')
        t.name = a_dict.get('name')
        t.description = a_dict.get('description')
        t.url = a_dict.get('url')

        return t

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "project_name": self.project_name,
            "creation_date": str(self.creation_date),
            "url": self.url
        }

    def format_http(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "project_name": self.project_name,
            "description": self.description,
            "creation_date": str(self.creation_date),
            "url": self.url,
        }


class Testcases(object):
    def __init__(self, testcases=list()):
        self.testcases = testcases

    @staticmethod
    def from_dict(res_dict):
        if res_dict is None:
            return None

        res = Testcases()
        for testcase in res_dict.get('testcases'):
            res.testcases.append(Testcase.from_dict(testcase))
        return res
