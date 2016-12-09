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
class TestcaseCreateRequest(object):
    def __init__(self, name, url=None, description=None,
                 tier=None, ci_loop=None, criteria=None,
                 blocking=None, dependencies=None, run=None,
                 domains=None, tags=None, version=None):
        self.name = name
        self.url = url
        self.description = description
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

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
        }


@swagger.model()
class TestcaseUpdateRequest(object):
    def __init__(self, name=None, description=None, project_name=None,
                 tier=None, ci_loop=None, criteria=None,
                 blocking=None, dependencies=None, run=None,
                 domains=None, tags=None, version=None, trust=None):
        self.name = name
        self.description = description
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

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "project_name": self.project_name,
            "tier": self.tier,
            "ci_loop": self.ci_loop,
            "criteria": self.criteria,
            "blocking": self.blocking,
            "dependencies": self.dependencies,
            "run": self.run,
            "domains": self.domains,
            "tags": self.tags,
            "version": self.version,
            "trust": self.trust
        }


@swagger.model()
class Testcase(object):
    def __init__(self, _id=None, name=None, project_name=None,
                 description=None, url=None, creation_date=None,
                 tier=None, ci_loop=None, criteria=None,
                 blocking=None, dependencies=None, run=None,
                 domains=None, tags=None, version=None,
                 trust=None):
        self._id = None
        self.name = None
        self.project_name = None
        self.description = None
        self.url = None
        self.creation_date = None
        self.tier=None
        self.ci_loop=None
        self.criteria=None
        self.blocking=None
        self.dependencies=None
        self.run=None
        self.domains=None
        self.tags=None
        self.version=None
        self.trust=None

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
        t.tier = a_dict.get('tier')
        t.ci_loop = a_dict.get('ci_loop')
        t.criteria = a_dict.get('criteria')
        t.blocking = a_dict.get('blocking')
        t.dependencies = a_dict.get('dependencies')
        t.run = a_dict.get('run')
        t.domains = a_dict.get('domains')
        t.tags = a_dict.get('tags')
        t.version = a_dict.get('version')
        t.trust = a_dict.get('trust')

        return t

    def format(self):
        return {
            "name": self.name,
            "description": self.description,
            "project_name": self.project_name,
            "creation_date": str(self.creation_date),
            "url": self.url,
            "tier": self.tier,
            "ci_loop": self.ci_loop,
            "criteria": self.criteria,
            "blocking": self.blocking,
            "dependencies": self.dependencies,
            "run": self.run,
            "domains": self.domains,
            "tags": self.tags,
            "version": self.version,
            "trust": self.trust
        }

    def format_http(self):
        return {
            "_id": str(self._id),
            "name": self.name,
            "project_name": self.project_name,
            "description": self.description,
            "creation_date": str(self.creation_date),
            "url": self.url,
            "tier": self.tier,
            "ci_loop": self.ci_loop,
            "criteria": self.criteria,
            "blocking": self.blocking,
            "dependencies": self.dependencies,
            "run": self.run,
            "domains": self.domains,
            "tags": self.tags,
            "version": self.version,
            "trust": self.trust
        }


@swagger.model()
class Testcases(object):
    """
        @property testcases:
        @ptype testcases: C{list} of L{Testcase}
    """
    def __init__(self):
        self.testcases = list()

    @staticmethod
    def from_dict(res_dict):
        if res_dict is None:
            return None

        res = Testcases()
        for testcase in res_dict.get('testcases'):
            res.testcases.append(Testcase.from_dict(testcase))
        return res
