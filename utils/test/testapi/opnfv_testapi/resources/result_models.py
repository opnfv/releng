##############################################################################
# Copyright (c) 2015 Orange
# guyrodrigue.koffi@orange.com / koffirodrigue@gmail.com
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from opnfv_testapi.resources import models
from opnfv_testapi.tornado_swagger import swagger


@swagger.model()
class TIHistory(models.ModelBase):
    """
        @ptype step: L{float}
    """
    def __init__(self, date=None, step=0):
        self.date = date
        self.step = step


@swagger.model()
class TI(models.ModelBase):
    """
        @property histories: trust_indicator update histories
        @ptype histories: C{list} of L{TIHistory}
        @ptype current: L{float}
    """
    def __init__(self, current=0):
        self.current = current
        self.histories = list()

    @staticmethod
    def attr_parser():
        return {'histories': TIHistory}


@swagger.model()
class ResultCreateRequest(models.ModelBase):
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
                 user=None,
                 public="true",
                 review="false",
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
        self.user = user
        self.public = public
        self.review = review
        self.trust_indicator = trust_indicator if trust_indicator else TI(0)


@swagger.model()
class ResultUpdateRequest(models.ModelBase):
    """
        @property trust_indicator:
        @ptype trust_indicator: L{TI}
    """
    def __init__(self, trust_indicator=None):
        self.trust_indicator = trust_indicator


@swagger.model()
class TestResult(models.ModelBase):
    """
        @property trust_indicator: used for long duration test case
        @ptype trust_indicator: L{TI}
    """
    def __init__(self, _id=None, case_name=None, project_name=None,
                 pod_name=None, installer=None, version=None,
                 start_date=None, stop_date=None, details=None,
                 build_tag=None, scenario=None, criteria=None,
                 user=None, public="true", review="false", trust_indicator=None):
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
        self.user = user
        self.public = public
        self.review = review
        self.trust_indicator = trust_indicator

    @staticmethod
    def attr_parser():
        return {'trust_indicator': TI}


@swagger.model()
class TestResults(models.ModelBase):
    """
        @property results:
        @ptype results: C{list} of L{TestResult}
    """
    def __init__(self):
        self.results = list()

    @staticmethod
    def attr_parser():
        return {'results': TestResult}
