##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


class Pod:
    """ describes a POD platform """
    def __init__(self):
        self._id = ""
        self.name = ""
        self.creation_date = ""

    @staticmethod
    def pod_from_dict(pod_dict):
        if pod_dict is None:
            return None

        p = Pod()
        p._id = pod_dict.get('_id')
        p.creation_date = pod_dict.get('creation_date')
        p.name = pod_dict.get('name')
        return p

    def format(self):
        return {
            "_id": self._id,
            "name": self.name,
            "creation_date": str(self.creation_date),
        }


class TestProject:
    """ Describes a test project"""

    def __init__(self):
        self._id = None
        self.name = None
        self.description = None
        self.creation_date = None

    @staticmethod
    def testproject_from_dict(testproject_dict):

        if testproject_dict is None:
            return None

        t = TestProject()
        t._id = testproject_dict.get('_id')
        t.creation_date = testproject_dict.get('creation_date')
        t.name = testproject_dict.get('name')
        t.description = testproject_dict.get('description')

        return t

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "creation_date": str(self.creation_date)
        }

    def format_http(self, test_cases=0):
        return {
            "_id": str(self._id),
            "name": self.name,
            "description": self.description,
            "creation_date": str(self.creation_date),
            "test_cases": test_cases
        }


class TestCase:
    """ Describes a test case"""

    def __init__(self):
        self._id = None
        self.name = None
        self.project_name = None
        self.description = None
        self.creation_date = None

    @staticmethod
    def test_case_from_dict(testcase_dict):

        if testcase_dict is None:
            return None

        t = TestCase()
        t._id = testcase_dict.get('_id')
        t.project_name = testcase_dict.get('project_name')
        t.creation_date = testcase_dict.get('creation_date')
        t.name = testcase_dict.get('name')
        t.description = testcase_dict.get('description')

        return t

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "project_name": self.project_name,
            "creation_date": str(self.creation_date)
        }

    def format_http(self, test_project=None):
        res = {
            "_id": str(self._id),
            "name": self.name,
            "description": self.description,
            "creation_date": str(self.creation_date),
        }
        if not (test_project is None):
            res["test_project"] = test_project

        return res


class TestResult:
    """ Describes a test result"""

    def __init__(self):
        self._id = None
        self.case_name = None
        self.project_name = None
        self.pod_id = None
        self.description = None
        self.creation_date = None
        self.details = None

    @staticmethod
    def test_result_from_dict(test_result_dict):

        if test_result_dict is None:
            return None

        t = TestResult()
        t._id = test_result_dict.get('_id')
        t.case_name = test_result_dict.get('case_name')
        t.project_name = test_result_dict.get('project_name')
        t.pod_id = test_result_dict.get('pod_id')
        t.description = test_result_dict.get('description')
        t.creation_date = str(test_result_dict.get('creation_date'))
        t.details = test_result_dict.get('details')

        return t

    def format(self):
        return {
            "case_name": self.case_name,
            "project_name": self.project_name,
            "pod_id": self.pod_id,
            "description": self.description,
            "creation_date": self.creation_date,
            "details": self.details,
        }

    def format_http(self):
        return {
            "_id": str(self._id),
            "case_name": self.case_name,
            "project_name": self.project_name,
            "pod_id": self.pod_id,
            "description": self.description,
            "creation_date": self.creation_date,
            "details": self.details,
        }
