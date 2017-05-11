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
class TestcaseCreateRequest(models.ModelBase):
    def __init__(self, name, url=None, description=None,
                 catalog_description=None, tier=None, ci_loop=None,
                 criteria=None, blocking=None, dependencies=None, run=None,
                 domains=None, tags=None, version=None):
        self.name = name
        self.url = url
        self.description = description
        self.catalog_description = catalog_description
        self.tier = tier
        self.ci_loop = ci_loop
        self.criteria = criteria
        self.blocking = blocking
        self.dependencies = dependencies
        self.run = run
        self.domains = domains
        self.tags = tags
        self.version = version
        self.trust = "Silver"


@swagger.model()
class TestcaseUpdateRequest(models.ModelBase):
    def __init__(self, name=None, description=None, project_name=None,
                 catalog_description=None, tier=None, ci_loop=None,
                 criteria=None, blocking=None, dependencies=None, run=None,
                 domains=None, tags=None, version=None, trust=None):
        self.name = name
        self.description = description
        self.catalog_description = catalog_description
        self.project_name = project_name
        self.tier = tier
        self.ci_loop = ci_loop
        self.criteria = criteria
        self.blocking = blocking
        self.dependencies = dependencies
        self.run = run
        self.domains = domains
        self.tags = tags
        self.version = version
        self.trust = trust


@swagger.model()
class Testcase(models.ModelBase):
    def __init__(self, _id=None, name=None, project_name=None,
                 description=None, url=None, creation_date=None,
                 catalog_description=None, tier=None, ci_loop=None,
                 criteria=None, blocking=None, dependencies=None, run=None,
                 domains=None, tags=None, version=None,
                 trust=None):
        self._id = None
        self.name = None
        self.project_name = None
        self.description = None
        self.catalog_description = None
        self.url = None
        self.creation_date = None
        self.tier = None
        self.ci_loop = None
        self.criteria = None
        self.blocking = None
        self.dependencies = None
        self.run = None
        self.domains = None
        self.tags = None
        self.version = None
        self.trust = None


@swagger.model()
class Testcases(models.ModelBase):
    """
        @property testcases:
        @ptype testcases: C{list} of L{Testcase}
    """
    def __init__(self):
        self.testcases = list()

    @staticmethod
    def attr_parser():
        return {'testcases': Testcase}
