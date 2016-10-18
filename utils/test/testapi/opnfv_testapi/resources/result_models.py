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
class TIHistory(object):
    """
        @ptype step: L{float}
    """
    def __init__(self, date=None, step=0):
        self.date = date
        self.step = step

    def format(self):
        return {
            "date": self.date,
            "step": self.step
        }

    @staticmethod
    def from_dict(a_dict):
        if a_dict is None:
            return None

        return TIHistory(a_dict.get('date'), a_dict.get('step'))


@swagger.model()
class TI(object):
    """
        @property histories: trust_indicator update histories
        @ptype histories: C{list} of L{TIHistory}
        @ptype current: L{float}
    """
    def __init__(self, current=0):
        self.current = current
        self.histories = list()

    def format(self):
        hs = []
        for h in self.histories:
            hs.append(h.format())

        return {
            "current": self.current,
            "histories": hs
        }

    @staticmethod
    def from_dict(a_dict):
        t = TI()
        if a_dict:
            t.current = a_dict.get('current')
            if 'histories' in a_dict.keys():
                for history in a_dict.get('histories', None):
                    t.histories.append(TIHistory.from_dict(history))
            else:
                t.histories = []
        return t


@swagger.model()
class ResultCreateRequest(object):
    """
        @property trust_indicator:
        @ptype trust_indicator: L{TI}
    """
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
        self.trust_indicator = trust_indicator if trust_indicator else TI(0)

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
            "trust_indicator": self.trust_indicator.format()
        }


@swagger.model()
class ResultUpdateRequest(object):
    """
        @property trust_indicator:
        @ptype trust_indicator: L{TI}
    """
    def __init__(self, trust_indicator=None):
        self.trust_indicator = trust_indicator

    def format(self):
        return {
            "trust_indicator": self.trust_indicator.format(),
        }


@swagger.model()
class TestResult(object):
    """
        @property trust_indicator: used for long duration test case
        @ptype trust_indicator: L{TI}
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
        t.trust_indicator = TI.from_dict(a_dict.get('trust_indicator'))
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
            "trust_indicator": self.trust_indicator.format()
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
            "trust_indicator": self.trust_indicator.format()
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
