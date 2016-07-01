##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from opnfv_testapi.tornado_swagger import swagger


@swagger.model()
class ResultCreateRequest(object):
    def __init__(self,
                 pod_name=None,
                 project_name=None,
                 case_name=None,
                 installer=None,
                 version=None,
                 start_date=None,
                 stop_date=None,
                 details=None,
                 build_tag=None,
                 scenario=None,
                 criteria=None,
                 trust_indicator=None):
        self.pod_name = pod_name
        self.project_name = project_name
        self.case_name = case_name
        self.installer = installer
        self.version = version
        self.start_date = start_date
        self.stop_date = stop_date
        self.details = details
        self.build_tag = build_tag
        self.scenario = scenario
        self.criteria = criteria
        self.trust_indicator = trust_indicator

    def format(self):
        return {
            "pod_name": self.pod_name,
            "project_name": self.project_name,
            "case_name": self.case_name,
            "installer": self.installer,
            "version": self.version,
            "start_date": self.start_date,
            "stop_date": self.stop_date,
            "details": self.details,
            "build_tag": self.build_tag,
            "scenario": self.scenario,
            "criteria": self.criteria,
            "trust_indicator": self.trust_indicator
        }


class ResultUpdateRequest(object):
    def __init__(self, trust_indicator=0):
        self.trust_indicator = trust_indicator

    def format(self):
        return {
            "trust_indicator": self.trust_indicator,
        }


@swagger.model()
class TestResult(object):
    """
        @property trust_indicator: must be int/long/float
        @ptype trust_indicator: L{float}
    """
    def __init__(self, _id=None, case_name=None, project_name=None,
                 pod_name=None, installer=None, version=None,
                 start_date=None, stop_date=None, details=None,
                 build_tag=None, scenario=None, criteria=None,
                 trust_indicator=None):
        self._id = _id
        self.case_name = case_name
        self.project_name = project_name
        self.pod_name = pod_name
        self.installer = installer
        self.version = version
        self.start_date = start_date
        self.stop_date = stop_date
        self.details = details
        self.build_tag = build_tag
        self.scenario = scenario
        self.criteria = criteria
        self.trust_indicator = trust_indicator

    @staticmethod
    def from_dict(a_dict):

        if a_dict is None:
            return None

        t = TestResult()
        t._id = a_dict.get('_id')
        t.case_name = a_dict.get('case_name')
        t.pod_name = a_dict.get('pod_name')
        t.project_name = a_dict.get('project_name')
        t.start_date = str(a_dict.get('start_date'))
        t.stop_date = str(a_dict.get('stop_date'))
        t.details = a_dict.get('details')
        t.version = a_dict.get('version')
        t.installer = a_dict.get('installer')
        t.build_tag = a_dict.get('build_tag')
        t.scenario = a_dict.get('scenario')
        t.criteria = a_dict.get('criteria')
        # 0 < trust indicator < 1
        # if bad value =>  set this indicator to 0
        t.trust_indicator = a_dict.get('trust_indicator')
        if t.trust_indicator is not None:
            if isinstance(t.trust_indicator, (int, long, float)):
                if t.trust_indicator < 0:
                    t.trust_indicator = 0
                elif t.trust_indicator > 1:
                    t.trust_indicator = 1
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
            "start_date": str(self.start_date),
            "stop_date": str(self.stop_date),
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
            "start_date": str(self.start_date),
            "stop_date": str(self.stop_date),
            "version": self.version,
            "installer": self.installer,
            "details": self.details,
            "build_tag": self.build_tag,
            "scenario": self.scenario,
            "criteria": self.criteria,
            "trust_indicator": self.trust_indicator
        }


@swagger.model()
class TestResults(object):
    """
        @property results:
        @ptype results: C{list} of L{TestResult}
    """
    def __init__(self):
        self.results = list()

    @staticmethod
    def from_dict(a_dict):
        if a_dict is None:
            return None

        res = TestResults()
        for result in a_dict.get('results'):
            res.results.append(TestResult.from_dict(result))
        return res
