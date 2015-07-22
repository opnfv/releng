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
        self._id = ""
        self.name = ""
        self.description = ""
        self.creation_date = ""

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
        self._id = ""
        self.name = ""
        self.test_project = ""
        self.description = ""
        self.creation_date = ""


class TestResult:
    """ Describes a test result"""
    def __init__(self):
        self._id = ""
        self.name = ""
        self.test_case = ""
        self.description = ""
        self.creation_date = ""