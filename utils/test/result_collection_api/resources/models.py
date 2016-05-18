##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################


class MetaCreateResponse(object):
    def __init__(self, success=True, uri=''):
        self.success = success
        self.uri = uri

    @staticmethod
    def from_dict(meta_dict):
        if meta_dict is None:
            return None

        meta = MetaCreateResponse()
        meta.success = meta_dict.get('success')
        meta.uri = meta_dict.get('uri')
        return meta


class MetaGetResponse(object):
    def __init__(self, success=True, total=0):
        self.success = success
        self.total = total

    @staticmethod
    def from_dict(meta_dict):
        if meta_dict is None:
            return None

        meta = MetaGetResponse()
        meta.success = meta_dict.get('success')
        meta.total = meta_dict.get('total')
        return meta


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
        }


class TestCase:
    """ Describes a test case"""

    def __init__(self):
        self._id = None
        self.name = None
        self.project_name = None
        self.description = None
        self.url = None
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
        t.url = testcase_dict.get('url')

        return t

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "project_name": self.project_name,
            "creation_date": str(self.creation_date),
            "url": self.url
        }

    def format_http(self, test_project=None):
        res = {
            "_id": str(self._id),
            "name": self.name,
            "description": self.description,
            "creation_date": str(self.creation_date),
            "url": self.url,
        }
        if test_project is not None:
            res["test_project"] = test_project

        return res


class TestResult:
    """ Describes a test result"""

    def __init__(self):
        self._id = None
        self.case_name = None
        self.project_name = None
        self.pod_name = None
        self.installer = None
        self.version = None
        self.description = None
        self.creation_date = None
        self.details = None
        self.build_tag = None
        self.scenario = None
        self.criteria = None
        self.trust_indicator = None

    @staticmethod
    def test_result_from_dict(test_result_dict):

        if test_result_dict is None:
            return None

        t = TestResult()
        t._id = test_result_dict.get('_id')
        t.case_name = test_result_dict.get('case_name')
        t.pod_name = test_result_dict.get('pod_name')
        t.project_name = test_result_dict.get('project_name')
        t.description = test_result_dict.get('description')
        t.creation_date = str(test_result_dict.get('creation_date'))
        t.details = test_result_dict.get('details')
        t.version = test_result_dict.get('version')
        t.installer = test_result_dict.get('installer')
        t.build_tag = test_result_dict.get('build_tag')
        t.scenario = test_result_dict.get('scenario')
        t.criteria = test_result_dict.get('criteria')
        # 0 < trust indicator < 1
        # if bad value =>  set this indicator to 0
        if test_result_dict.get('trust_indicator') is not None:
            if isinstance(test_result_dict.get('trust_indicator'),
                          (int, long, float)):
                if test_result_dict.get('trust_indicator') < 0:
                    t.trust_indicator = 0
                elif test_result_dict.get('trust_indicator') > 1:
                    t.trust_indicator = 1
                else:
                    t.trust_indicator = test_result_dict.get('trust_indicator')
            else:
                t.trust_indicator = 0
        else:
            t.trust_indicator = 0
        return t

    def format(self):
        return {
            "case_name": self.case_name,
            "project_name": self.project_name,
            "pod_name": self.pod_name,
            "description": self.description,
            "creation_date": str(self.creation_date),
            "version": self.version,
            "installer": self.installer,
            "details": self.details,
            "build_tag": self.build_tag,
            "scenario": self.scenario,
            "criteria": self.criteria,
            "trust_indicator": self.trust_indicator
        }

    def format_http(self):
        return {
            "_id": str(self._id),
            "case_name": self.case_name,
            "project_name": self.project_name,
            "pod_name": self.pod_name,
            "description": self.description,
            "creation_date": str(self.creation_date),
            "version": self.version,
            "installer": self.installer,
            "details": self.details,
            "build_tag": self.build_tag,
            "scenario": self.scenario,
            "criteria": self.criteria,
            "trust_indicator": self.trust_indicator
        }
